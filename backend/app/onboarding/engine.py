import logging
logger = logging.getLogger(__name__)

import os
from typing import List, Optional, Tuple
from llama_index import ServiceContext, StorageContext, VectorStoreIndex
from llama_index.vector_stores.pinecone import PineconeVectorStore
from beanie.odm.operators.find.logical import And
from beanie.operators import In
from beanie.odm.enums import SortDirection

from app.onboarding.reader import YTChannelReader
from app.onboarding import yt_utils
from app.db.models import (
                        Channel, 
                        ChannelOnBoardingRequest,
                        ChannelOnBoardingRequestStatusEnum,
                        ChannelStatusEnum,
                        User
                        )

async def search_for_channels(query: str, region: Optional[str]='US', limit: Optional[int]=5) -> List[Channel]:
    """
    Search for channels based on a query.

    Args:
        query (str): The query to search for.
        region (str, optional): The region to search in. Defaults to 'US'.
        limit (int, optional): The maximum number of results to return. Defaults to 5.

    Returns:
        List[Channel]: A list of channels that match the query.
    """
    try:
        channel_list = yt_utils.search_channels(query, region, limit)
    
        channels = []
        if channel_list:
            channels = [Channel(id=channel['id'],
                                title=channel['title'],
                                description=" ".join([s['text'] for s in channel['descriptionSnippet']])
                                if channel['descriptionSnippet'] else "",
                                url=channel['link'],
                                thumbnails=channel['thumbnails'],
                                status= ChannelStatusEnum.INACTIVE
                                ) 
                                for channel in channel_list
                        ]
        return channels
    except Exception as e:
        logger.error(f"channel search failed for query: {query}", e)
        raise e
    
async def get_channels(channel_ids: List[str]) -> Tuple[List[Channel], List[str]]:
    """
    Retrieve channels by their IDs.

    Args:
    - channel_ids (List[str]): The IDs of the channels to retrieve.

    Returns:
    - Tuple[List[Channel], List[str]]: A tuple containing the active channels with the specified IDs and a list of missing channel IDs.
    """
    # Retrieve active channels
    channels = await Channel.find(In(Channel.id, channel_ids)).to_list()
    
    # Find missing channel IDs
    missing_channel_ids = [channel_id for channel_id in channel_ids if channel_id not in [c.id for c in channels]]
    
    return channels, missing_channel_ids


async def get_default_channels(limit:int=5) -> List[Channel]:
    """
    Retrieve a list of default channels with the given limit.

    Args:
        limit (int): The maximum number of channels to retrieve.

    Returns:
        List[Channel]: A list of default channels.
    """
    return await Channel.find(
        Channel.status == ChannelStatusEnum.ACTIVE,
        limit=limit,
        sort=[("updated_at", SortDirection.ASCENDING)]
    ).to_list()

async def get_user_channels(user_session_id: str) -> List[Channel]:
    """
    Retrieve the channels added by the user.

    Args:
        user_session_id (str): The ID of the user's session.

    Returns:
        List[Channel]: A list of Channel objects added by the user.
    """

    # Check if the user session ID is provided
    if user_session_id:
        # Retrieve the user based on the session ID
        user = await User.get(user_session_id)
        # If the user exists and has added channels, return the user's channels
        if user and user.channels:
            channels, _ = await get_channels(list(user.channels))
            return channels

    # If no user session ID is provided or the user has not added any channels,
    # return default channels
    return await get_default_channels(limit=5)
    

async def create_onboarding_request(channel_id: str, requested_by: str) -> ChannelOnBoardingRequest:
    """
    Asynchronously creates an onboarding request for a specific channel.

    Args:
        channel_id (str): The ID of the channel for which the onboarding request is being created.
        requested_by (str): The user who is requesting the onboarding.

    Returns:
        bool: The ID of the created onboarding request.
    """

    # Create a new onboarding request for the specified channel and user
    try:
        #
        channel = await Channel.get(channel_id)
        if not channel:
            channel_info = yt_utils.get_channel_info(channel_id)
            channel = Channel(id=channel_info['id'],
                            title=channel_info['title'],
                            description=channel_info['description'],
                            url=channel_info['url'],
                            thumbnails=channel_info['thumbnails'],
                            status=ChannelStatusEnum.INACTIVE
                            )
            await channel.save()
            
        # Add channel to user
        user = await User.get(requested_by)
        user.channels.add(channel.id)
        await user.save()

        request = ChannelOnBoardingRequest(
            channel_id=channel_id,
            requested_by=requested_by,
            status=ChannelOnBoardingRequestStatusEnum.PENDING 
            if channel.status != ChannelStatusEnum.ACTIVE 
            else ChannelOnBoardingRequestStatusEnum.AUTOCOMPLETED
        )
        # Insert the request into the database
        request = await request.insert()
        # Return the ID of the created onboarding request
        return request
    except Exception as e:
        logger.error(f"Failed to create onboarding request for {channel_id} as requested by {requested_by}", e)
        raise e

async def process_onboarding_request(request: ChannelOnBoardingRequest) -> None:
    """
    Process the onboarding request for a channel.

    Args:
        request_id (str): The ID of the onboarding request to be processed.

    Returns:
        None
    """
    # Retrieve channel information and create a new Channel object
    try:
        request.status = ChannelOnBoardingRequestStatusEnum.PROCESSING
        await request.save()
        channel = Channel.get(request.channel_id)
        if not channel:
            channel_info = yt_utils.get_channel_info(request.channel_id)
            channel = Channel(id=channel_info['id'],
                            title=channel_info['title'],
                            description=channel_info['description'],
                            url=channel_info['url'],
                            thumbnails=channel_info['thumbnails'],
                            status=ChannelStatusEnum.INACTIVE
                            )
            await channel.save()

        if channel.status == ChannelStatusEnum.ACTIVE:
            request.status = ChannelOnBoardingRequestStatusEnum.COMPLETED
            await request.save()
            return

        # Retrieve documents for the channel
        video_documents = YTChannelReader(channel).load_data(min_duration=60, languages_preference=["en","en-IN"])
        logger.info(f"Retrieved {len(video_documents)} videos with transcripts for channel: {request.channel_id}")

        # Check if videos are found for the channel
        if not video_documents:
            request.status = ChannelOnBoardingRequestStatusEnum.FAILED
            await request.save()
            raise ValueError(f"No videos found for the channel: {request.channel_id}")

        # Set up service and storage contexts
        service_context = ServiceContext.from_defaults(chunk_size=1000)

        vector_store = PineconeVectorStore(api_key=os.environ['PINECONE_API_KEY'],
                                        index_name=os.environ['VECTOR_STORE_INDEX_NAME'],
                                        namespace=channel.id
                                            )
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # Index the documents in the vector store
        VectorStoreIndex.from_documents(video_documents,
                                    storage_context=storage_context,
                                    service_context=service_context)
        
        channel.status = ChannelStatusEnum.ACTIVE
        await channel.save()

        # Update the status of the onboarding request to COMPLETED
        request.status = ChannelOnBoardingRequestStatusEnum.COMPLETED
        await request.save()
    except Exception as e:
        # Update the status of the onboarding request to FAILED and raise the exception
        logger.error(f"Failed to process onboarding request {request.id}", e)
        request.status = ChannelOnBoardingRequestStatusEnum.FAILED
        await request.save()
        raise e