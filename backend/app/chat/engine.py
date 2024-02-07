import logging
logger = logging.getLogger(__name__)

import os
from click import UUID
from typing import List
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index import VectorStoreIndex
from llama_index.core.llms.types import ChatMessage
from llama_index.chat_engine.types import StreamingAgentChatResponse
from app.db.models import Channel, ChannelStatusEnum, Chat, ChatResponse, ChatResponseStatusEnum


async def create_new_chat(channel_id: str) -> UUID:
    """
    Create a new chat for the given channel ID.
    
    Args:
    - channel_id (str): The ID of the channel for which the chat is being created.
    
    Returns:
    - UUID: The ID of the newly created chat.
    
    Raises:
    - ValueError: If the channel is not found or not active, or if failed to create new chat.
    """
    try:
        # Get the channel with the specified ID
        channel = await Channel.get(channel_id)
        
        # Check if the channel exists
        if not channel:
            raise ValueError("Channel not found.")
        
        # Check if the channel is active
        if channel.status != ChannelStatusEnum.ACTIVE:
            raise ValueError("Channel is not active.")
        
        # Create a new chat with the channel ID as the vector index name and namespace
        chat = Chat(vector_index_name=os.environ['VECTOR_STORE_INDEX_NAME'],
                    vector_namespace=channel.id)

        # Save the new chat and return its ID if successful
        chat = await chat.save()
        return chat.id
    except Exception as e:
        logging.error(f"Failed to create new chat for channel {channel_id}", e)
        raise e

async def get_chat_history(chat_id: str) -> List[ChatResponse]:
    """
    Retrieve chat history based on the provided chat_id.

    Args:
    chat_id (str): The ID of the chat to retrieve history from.

    Returns:
    List[ChatResponse]: The chat history.

    Raises:
    ValueError: If the chat is not found.
    """
    try:
        # Retrieve the chat based on the provided chat_id
        chat = await Chat.get(chat_id)

        # Check if the chat is found
        if not chat:
            raise ValueError(f"Chat not found for chat {chat_id}")

        # Return the chat history
        return [c for c  in chat.chat_history if c.status == ChatResponseStatusEnum.COMPLETED]
    except Exception as e:
        # Log and raise the exception if failed to retrieve chat history
        logger.error(f"Failed to get chat history for chat {chat_id}", e)
        raise e
    
async def generate_chat_response_stream(chat: Chat, user_message:str) -> StreamingAgentChatResponse:
    """
    Generate a streaming chat response based on the user message.

    Args:
        chat (Chat): The chat object containing vector index name, namespace, and chat history.
        user_message (str): The user's message.

    Returns:
        StreamingAgentChatResponse: The streaming chat response.
    """
    try:
        # Set up the vector store using Pinecone API
        vector_store = PineconeVectorStore(
            api_key=os.environ['PINECONE_API_KEY'],
            index_name=chat.vector_index_name,
            namespace=chat.vector_namespace,
        )
        
        # Create an index from the vector store
        index = VectorStoreIndex.from_vector_store(vector_store)
        
        # Create a query engine from the index
        chat_engine = index.as_chat_engine(
            chat_mode=chat.chat_mode,
            kwargs=chat.chat_kwargs
        )

        # Query the channel and get the response
        return await chat_engine.astream_chat(
            user_message, 
            chat_history=[ChatMessage.parse_obj(c.model_dump())
                          for c in chat.chat_history
                          if c.status == ChatResponseStatusEnum.COMPLETED
                         ]
        )
    except Exception as e:
        logger.error(f"Failed to generate chat response for chat {chat.id}", e)
        raise e
