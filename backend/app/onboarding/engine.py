import logging
logger = logging.getLogger(__name__)

import os
from typing import List, Optional
from llama_index import ServiceContext, StorageContext, VectorStoreIndex
from llama_index.vector_stores.pinecone import PineconeVectorStore

from app.onboarding.reader import YTChannelReader
from app.onboarding import yt_utils
from app.db.models import (
                        Channel, 
                        ChannelOnBoardingRequest,
                        ChannelOnBoardingRequestStatus,
                        ChannelStatus
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
        for channel in channel_list:
            for thumbnail in channel['thumbnails']:
                thumbnail['url'] = "https:" + thumbnail['url'] if thumbnail['url'].startswith("//") else thumbnail['url']
        channels = [Channel(id=channel['id'],
                            title=channel['title'],
                            description=" ".join([s['text'] for s in channel['descriptionSnippet']]),
                            url=channel['link'],
                            thumbnails=channel['thumbnails']
                            ) 
                    for channel in channel_list
                    ]
        return channels
    except Exception as e:
        logger.error(f"channel search failed for query: {query}", e)
        raise e
    

async def create_onboarding_request(channel_id: str, requested_by: str) -> ChannelOnBoardingRequest:
    """
    Asynchronously creates an onboarding request for a specific channel.

    Args:
        channel_id (str): The ID of the channel for which the onboarding request is being created.
        requested_by (str): The user who is requesting the onboarding.

    Returns:
        bool: The ID of the created onboarding request.
    """
    #TODO: Add error handling

    # Create a new onboarding request for the specified channel and user
    try:
        request = ChannelOnBoardingRequest(
            channel_id=channel_id,
            requested_by=requested_by,
            status=ChannelOnBoardingRequestStatus.PENDING
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
        request.status = ChannelOnBoardingRequestStatus.PROCESSING
        await request.save()

        channel_info = yt_utils.get_channel_info(request.channel_id)
        channel = Channel(id=channel_info['id'],
                        title=channel_info['title'],
                        description=channel_info['description'],
                        url=channel_info['url'],
                        thumbnails=channel_info['thumbnails'],
                        status=ChannelStatus.INACTIVE
                        )
        
        # Retrieve documents for the channel
        video_documents = YTChannelReader(channel).load_data(min_duration=60, languages_preference=["en","en-IN"])
        logger.info(f"Retrieved {len(video_documents)} videos with transcripts for channel: {request.channel_id}")

        # Check if videos are found for the channel
        if not video_documents:
            request.status = ChannelOnBoardingRequestStatus.FAILED
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
        
        channel.status = ChannelStatus.ACTIVE
        await channel.save()

        # Update the status of the onboarding request to COMPLETED
        request.status = ChannelOnBoardingRequestStatus.COMPLETED
        await request.save()
    except Exception as e:
        # Update the status of the onboarding request to FAILED and raise the exception
        logger.error(f"Failed to process onboarding request {request.id}", e)
        request.status = ChannelOnBoardingRequestStatus.FAILED
        await request.save()
        raise e