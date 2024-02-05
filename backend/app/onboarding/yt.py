from youtube_transcript_api import YouTubeTranscriptApi, TranscriptList, Transcript
from youtube_transcript_api._errors import YouTubeRequestFailed, TooManyRequests
from typing import List
import youtubesearchpython as yps
from tenacity import retry, stop_after_attempt, wait_random, retry_if_exception
import logging
logger = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(5), wait=wait_random(min=1, max=3))
def get_channel_info(channel_id: str) -> dict:
    """
    Retrieve information about a channel using its ID.

    Args:
        channel_id (str): The ID of the channel to retrieve information for.

    Returns:
        dict: A dictionary containing the information about the channel.
    """
    return yps.Channel.get(channel_id)

@retry(stop=stop_after_attempt(5), wait=wait_random(min=1, max=3))
def fetch_playlist(channel_id: str) -> yps.Playlist:
    """
    Fetches a playlist for a given channel ID and returns a Playlist object.
    
    Args:
    channel_id (str): The ID of the channel
    
    Returns:
    Playlist: The playlist for the given channel ID
    """
    return yps.Playlist(yps.playlist_from_channel_id(channel_id))

@retry(stop=stop_after_attempt(5), wait=wait_random(min=1, max=3),
       retry=(retry_if_exception(YouTubeRequestFailed) | retry_if_exception(TooManyRequests))
       )
def list_transcripts(video_id: str) -> TranscriptList:
    """
    Fetches the list of transcripts for a given video ID.

    Args:
        video_id (str): The ID of the YouTube video.

    Returns:
        list: A list of transcript objects.
    """
    return YouTubeTranscriptApi.list_transcripts(video_id=video_id)

@retry(stop=stop_after_attempt(5), wait=wait_random(min=1, max=3),
       retry=(retry_if_exception(YouTubeRequestFailed) | retry_if_exception(TooManyRequests))
       )
def fetch_transcript(transcript: Transcript) -> str:
    """
    Retries fetching the transcript up to 5 attempts with random wait time between 1 and 3 seconds.

    Args:
    - transcript (Transcript): The transcript to fetch.

    Returns:
    - str: The fetched transcript.
    """
    return transcript.fetch()
    

def download_transcript(video_id, languages=['en','en-IN']):
    """
    Download transcript for the specified video in the given languages.
    
    Args:
        video_id (str): The ID of the video.
        languages (list): A list of language codes for the desired transcripts. Defaults to ['en', 'en-IN'].
        
    Returns:
        dict: The downloaded transcript data.
        
    Raises:
        ValueError: If the transcript download fails.
    """
    try:
        # Get the list of available transcripts for the video
        transcript_list = list_transcripts(video_id)
        
        # Check for manually created transcripts
        manual_langs = set(transcript_list._manually_created_transcripts.keys())
        if set(languages).intersection(manual_langs):
            for lang in languages:
                if lang in manual_langs:
                    t = transcript_list.find_manually_created_transcript(language_codes=[lang])
                    data = fetch_transcript(t)
                    return data
        
        # Check for generated transcripts
        generated_langs = set(transcript_list._generated_transcripts.keys())
        if set(languages).intersection(generated_langs):
            for lang in languages:
                if lang in generated_langs:
                    t = transcript_list.find_generated_transcript(language_codes=[lang])
                    data = fetch_transcript(t)
                    return data
         
        # Check for translated transcripts
        translated_langs = set([t['language_code'] for t in transcript_list._translation_languages])
        if set(languages).intersection(translated_langs):
            for lang in languages:
                if lang in translated_langs:
                    t = t = transcript_list.find_transcript(language_codes=manual_langs.union(generated_langs)).translate(lang)
                    data = fetch_transcript(t)
                    return data
    except Exception as e:
        logger.error(e)
        raise ValueError(f"Failed to download transcript for video: {video_id}")
    
    raise ValueError(f"No transcripts found for video: {video_id}")
    
def get_channel_videos(channel_id: str) -> dict:
    try:
        # Retrieve the playlist for the given channel
        playlist = fetch_playlist(channel_id)
        # Keep fetching videos until there are no more left in the playlist
        while playlist.hasMoreVideos:
            playlist.getNextVideos()
    except Exception as e:
        # Log an error if videos retrieval fails and re-raise the exception
        logger.error(e)
        raise ValueError(f"Failed to retrieve videos for channel: {channel_id}")

    # If no videos are found, log a message and return an empty list
    if not playlist.videos:
        raise ValueError("No videos found for channel: %s", channel_id)
    
    return playlist.videos
        