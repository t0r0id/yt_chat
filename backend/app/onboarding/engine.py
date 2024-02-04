
import logging
import os
from typing import List
from app.db.db import MongoDBClientSingleton
from app.onboarding.reader import YTTranscriptReader

import youtubesearchpython as yps
from youtube_transcript_api import YouTubeTranscriptApi
from llama_index import ServiceContext, StorageContext, VectorStoreIndex
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from app.db.models import (Video
                        , Channel
                        , TranscriptSegment
                        , ChannelOnBoardingRequest
                        , ChannelOnBoardingRequestStatus
                        , ChannelStatus
                        )


logger = logging.getLogger(__name__)

def get_channel_videos(channel: Channel) -> List[Video]:
    """
    Retrieves all videos from a given channel and returns a list of Video objects.

    Args:
        channel (Channel): The channel from which to retrieve videos.

    Returns:
        List[Video]: A list of Video objects from the specified channel.
    """
    # Retrieve the playlist for the given channel
    try:
        playlist = yps.Playlist(yps.playlist_from_channel_id(channel.id))
        # Keep fetching videos until there are no more left in the playlist
        while playlist.hasMoreVideos:
            playlist.getNextVideos()
    except Exception as e:
        # Log an error if videos retrieval fails and re-raise the exception
        logger.error(f"Failed to retrieve videos for channel: {channel.id}")
        raise e
    
    # If no videos are found, log a message and return an empty list
    if not playlist.videos:
        logger.info("No videos found for channel: %s", channel.id)
        return []

    # Log the number of retrieved videos and create Video objects
    logger.info("Retrieved %d videos for channel: %s", len(playlist.videos), channel.id)
    videos = [Video(id=video['id'],
                    title=video['title'],
                    channel=channel,
                    )
                for video in playlist.videos]

    # Retrieve and populate the transcript for each video
    for video in videos:
        try:
            #TODO: Enable loading translated transcripts
            video.transcript = [TranscriptSegment(text=segment['text'],
                                                start_ms=int(segment['start']*1000),
                                                end_ms=int((segment['start']
                                                            + segment['duration'])*1000))
                                for segment in 
                                YouTubeTranscriptApi.get_transcript(video.id, languages=['en'])]
        except Exception as e:
            # Log an error if transcript retrieval fails
            logger.error(f"Failed to retrieve transcript for video: {video.id}")

    # Return only the videos with a populated transcript
    return [video for video in videos if video.transcript]
        

async def process_onboarding_request(request_id: str):
    """
    Process the onboarding request for a channel.

    Args:
        request_id (str): The ID of the onboarding request to be processed.

    Returns:
        None
    """
    # Retrieve the onboarding request by ID
    request = await ChannelOnBoardingRequest.get(request_id)

    # Check if the request exists
    if not request:
        raise ValueError(f"Onboarding request ({request_id}) not found")

    # Check if the request is in the QUEUED state
    if request.status != ChannelOnBoardingRequestStatus.QUEUED:
        raise ValueError(f"Onboarding request ({request.id}) is not in the QUEUED state. Request status: {request.status}")

    # Check if the channel has already been onboarded
    if await Channel.find_one(Channel.id == request.channel_id):
        logger.debug(f"Channel ({request.channel_id}) has already been onboarded: Request_id:{request_id}")
        return

    # Update the status of the onboarding request to PROCESSING
    logger.info(f"Onboarding request ({request.id}) is in the QUEUED state. Request status: {request.status}")
    request.status = ChannelOnBoardingRequestStatus.PROCESSING
    await request.save()

    # Retrieve channel information and create a new Channel object
    try:
        channel_info = yps.Channel.get(request.channel_id)
        channel = Channel(id=channel_info['id'],
                          title=channel_info['title'],
                          description=channel_info['description'],
                          url=channel_info['url'],
                          thumbnails=channel_info['thumbnails'],
                          status=ChannelStatus.INACTIVE)

        # Retrieve videos for the channel
        videos = get_channel_videos(channel)

        # Check if videos are found for the channel
        if not videos:
            request.status = ChannelOnBoardingRequestStatus.FAILED
            await request.save()
            raise ValueError(f"No videos found for the channel: {request.channel_id}")

        # Load transcripts for the videos
        documents = YTTranscriptReader(videos).load_data()

        # Set up service and storage contexts
        service_context = ServiceContext.from_defaults(chunk_size=1000)
        mongo_client = MongoDBClientSingleton.get_instance().client
        vector_store = MongoDBAtlasVectorSearch(mongo_client,
                                                db_name=os.environ['DB_NAME'],
                                                collection_name=os.environ['VECTOR_STORE_COLLECTION_NAME'],
                                                index_name=os.environ['VECTOR_STORE_INDEX_NAME'])
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # Index the documents in the vector store
        VectorStoreIndex.from_documents(documents,
                                       storage_context=storage_context,
                                       service_context=service_context)
        
        channel.status = ChannelStatus.ACTIVE
        await channel.save()

        # Update the status of the onboarding request to COMPLETED
        request.status = ChannelOnBoardingRequestStatus.COMPLETED
        await request.save()
    except Exception as e:
        # Update the status of the onboarding request to FAILED and raise the exception
        request.status = ChannelOnBoardingRequestStatus.FAILED
        await request.save()
        raise e
    
async def create_onboarding_request(channel_id: str, requested_by: str) -> bool:
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
    request = ChannelOnBoardingRequest(
        channel_id=channel_id,
        requested_by=requested_by,
        status=ChannelOnBoardingRequestStatus.PENDING
    )
    # Insert the request into the database
    request = await request.insert()
    # Return the ID of the created onboarding request
    return request.id

    
    