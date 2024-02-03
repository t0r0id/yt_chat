
import logging
from typing import List

import youtubesearchpython as yps
from youtube_transcript_api import YouTubeTranscriptApi

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
    try:
        playlist = yps.Playlist(yps.playlist_from_channel_id(channel.id))
        while playlist.hasMoreVideos:
            playlist.getNextVideos()
    except Exception as e:
        logger.error(f"Failed to retrieve videos for channel: {channel.id}")
        raise e
    
    if not playlist.videos:
        logger.info("No videos found for channel: %s", channel.id)
        return []

    logger.info("Retrieved %d videos for channel: %s", len(playlist.videos), channel.id)
    videos = [Video(id=video['id'],
                    title=video['title'],
                    channel=channel,
                    )
                for video in playlist.videos]

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
            logger.error(f"Failed to retrieve transcript for video: {video.id}")

    return [video for video in videos if video.transcript]
        

async def process_onboarding_request(request_id: str) -> bool:
    """
    Process the onboarding request for a channel.
    
    Args:
        request (ChannelOnBoardingRequest): The onboarding request to be processed.
        
    Returns:
        bool: True if the onboarding process is successful, False otherwise.
    """

    request = await ChannelOnBoardingRequest.get(request_id)

    if not request:
        logger.error(f"Onboarding request ({request_id}) not found")
        return False

    if request.status != ChannelOnBoardingRequestStatus.QUEUED:
        logger.error(f"Onboarding request ({request.id}) is not in the QUEUED state. Request status: {request.status}")
        return False
    
    if await Channel.find_one(Channel.id == request.channel_id):
        logger.info(f"Channel ({request.channel_id}) has already been onboarded: Request_id:{request_id}")
        return True

    logger.info(f"Onboarding request ({request.id}) is in the QUEUED state. Request status: {request.status}")
    request.status = ChannelOnBoardingRequestStatus.PROCESSING
    await request.save()

    try:
        channel_info = yps.Channel.get(request.channel_id)
        channel = Channel(id = channel_info['id']
                          , title = channel_info['title']
                          , description = channel_info['description']
                          , url = channel_info['url']
                          , thumbnails = channel_info['thumbnails']
                          , channel_status = ChannelStatus.ACTIVE
                          )
        
        videos = get_channel_videos(channel)
        if videos:
            await channel.save()
            await Video.insert_many(videos)

        #TODO: Add logic for creating veector embeddings

            request.status = ChannelOnBoardingRequestStatus.COMPLETED
            await request.save()
            return True

        request.status = ChannelOnBoardingRequestStatus.FAILED
        await request.save()
        return False
    except Exception as e:
        logger.error(f"Failed to onboard channel: {request.channel_id}")
        request.status = ChannelOnBoardingRequestStatus.FAILED
        await request.save()
        print(e)
        return False
    
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
    request = ChannelOnBoardingRequest(channel_id = channel_id
                                      , requested_by = requested_by
                                      , status = ChannelOnBoardingRequestStatus.PENDING
                                      )
    request = await request.insert()
    return request.id

    
    