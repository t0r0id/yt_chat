from llama_index.readers.schema.base import Document
from llama_index.readers.base import BaseReader
from typing import List
from app.db.models import Video

class YTTranscriptReader(BaseReader):
    """Class to convert Video objects to Document objects for reader."""
    
    def __init__(self, videos: List[Video]) -> None:
        super().__init__()
        self.videos = videos

    def load_data(
        self,
    ) -> List[Document]:
        """
        Load data from a list of videos and return a list of documents.
        
        Args:
            videos (List[Video]): A list of Video objects containing transcripts.
        
        Returns:
            List[Document]: A list of Document objects containing the transcribed text and extra information.
        """

        results = []
        for video in self.videos:
            chunk_text = [chunk.text for chunk in video.transcript]
            transcript = "\n".join(chunk_text)
            results.append(Document(text=transcript, extra_info={"video_id": video.id
                                                                 ,'video_title': video.title
                                                                 , "channel_id": video.channel.id
                                                                 ,'channel_title': video.channel.title
                                                                 }))
        return results
    
