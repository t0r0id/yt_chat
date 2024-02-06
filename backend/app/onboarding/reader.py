import logging
logger = logging.getLogger(__name__)

from typing import List, Any, Optional
from llama_index.readers.schema.base import Document
from llama_index.readers.base import BaseReader
from app.db.models import Channel, Video, TranscriptSegment
from app.onboarding import yt_utils

class YTChannelReader(BaseReader):
    """Class to convert YT channel id to Document objects for reader."""

    def __init__(self, channel: str) -> None:
        super().__init__()
        self.channel = channel
        
    def _fetch_videos(self, min_duration: int = 0
                      , languages_preference: List[str] = ["en","en-IN"]
                      ) -> List[Video]:
        """
        Retrieves all videos from a given channel and returns a list of Video objects.

        Args:
            channel (Channel): The channel from which to retrieve videos.

        Returns:
            List[Video]: A list of Video objects from the specified channel.
        """

        video_info_list = yt_utils.get_channel_videos(self.channel.id)
        # Log the number of retrieved videos and create Video objects
        logger.info("Retrieved %d videos for channel: %s", len(video_info_list), self.channel.id)
        videos = [Video(id=video['id'],
                        title=video['title'],
                        channel=self.channel,
                        duration=yt_utils.duration_str_to_seconds(video['duration']),
                        )
                    for video in video_info_list]

        # Filter out videos that are too short
        videos = [video for video in videos if video.duration > min_duration]

        logger.info(f"Retrieveing transcript for {len(videos)} videos from channel_id:{self.channel.id}")
        # Retrieve and populate the transcript for each video
        for video in videos:
            try:
                video.transcript = [
                    TranscriptSegment(text=segment['text'],
                                      start_ms=int(segment['start']*1000),
                                      end_ms=int((segment['start']
                                                  + segment['duration'])*1000))
                                    for segment in 
                                    yt_utils.download_transcript(video.id, languages=languages_preference)
                                    ]
            except Exception as e:
                # Log an error if transcript retrieval fails
                logger.error(f"Failed to retrieve transcript for video: {video.id}")

        # Return only the videos with a populated transcript
        return [video for video in videos if video.transcript]

    def load_data(
        self,
        min_duration: Optional[int],
        languages_preference: Optional[List[str]],
        **load_kwargs: Any,
    ) -> List[Document]:
        """
        Load data from a list of videos and return a list of documents.
        
        Args:
            videos (List[Video]): A list of Video objects containing transcripts.
        
        Returns:
            List[Document]: A list of Document objects containing the transcribed text and extra information.
        """
        videos = self._fetch_videos(min_duration=min_duration, languages_preference=languages_preference)
        results = []
        for video in videos:
            chunk_text = [chunk.text for chunk in video.transcript]
            transcript = "\n".join(chunk_text)
            results.append(Document(text=transcript, extra_info={"video_id": video.id
                                                                 ,'video_title': video.title
                                                                 , "channel_id": video.channel.id
                                                                 ,'channel_title': video.channel.title
                                                                 }))
        return results
    
