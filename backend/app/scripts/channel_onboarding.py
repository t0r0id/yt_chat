
import logging
from typing import List

import youtubesearchpython as yps

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
        playlist = yps.Playlist(yps.playlist_from_channel_id(channel.channel_id))
        while playlist.hasMoreVideos:
            playlist.getNextVideos()
    except Exception as e:
        logger.error(f"Failed to retrieve videos for channel: {channel.channel_id}")
        raise e
    
    if not playlist.videos:
        logger.info("No videos found for channel: %s", channel.channel_id)
        return []

    logger.info("Retrieved %d videos for channel: %s", len(playlist.videos), channel.channel_id)
    videos = [Video(video_id=video['id'],
                    title=video['title'],
                    channel=channel,
                    )
                for video in playlist.videos]

    for video in videos:
        video_url = f"https://www.youtube.com/watch?v={video.video_id}"
        try:
            video.transcript = [TranscriptSegment(text=segment['text'],
                                                start_ms=segment['startMs'],
                                                end_ms=segment['endMs'])
                                for segment in yps.Transcript.get(video_url).segments]
        except Exception as e:
            logger.info(f"Failed to retrieve transcript for video: {video_url}")

    return videos
        

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
        logger.info(f"Onboarding request ({request_id}) not found")
        return False

    if request.status !=  ChannelOnBoardingRequestStatus.QUEUED:
        logger.info(f"Onboarding request ({request.id}) is not in the QUEUED state. Request status: {request.status}")
        return False
    
    if Channel.find_one(Channel.channel_id == request.channel_id):
        logger.info(f"Channel ({request.channel_id}) has already been onboarded: Request_id:{request_id}")

    logger.info(f"Onboarding request ({request.id}) is in the QUEUED state. Request status: {request.status}")
    request.status = ChannelOnBoardingRequestStatus.PROCESSING
    request.save()

    try:
        channel_info = yps.Channel.get(request.channel_id)
        channel = Channel(channel_id = channel_info['id']
                          , title = channel_info['title']
                          , description = channel_info['description']
                          , url = channel_info['url']
                          , thumbnails = channel_info['thumbnails']
                          , channel_status = ChannelStatus.ACTIVE
                          )
        
        videos = get_channel_videos(channel)
        await channel.insert()
        await Video.insert_many(videos)

        #TODO: Add logic to upsert channel and videos to db

        request.status = ChannelOnBoardingRequestStatus.COMPLETED
        request.save()
        return True
    except Exception as e:
        logger.error(f"Failed to onboard channel: {request.channel_id}")
        request.status = ChannelOnBoardingRequestStatus.FAILED
        request.save()
        print(e)
        return False
    
async def create_onboarding_request(channel_id: str, requested_by: str) -> bool:
    request = ChannelOnBoardingRequest(channel_id = channel_id
                                      , requested_by = requested_by
                                      , status = ChannelOnBoardingRequestStatus.PENDING
                                      )
    request = await request.insert()
    return request.id

    
    