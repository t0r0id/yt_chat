import logging
logger = logging.getLogger(__name__)

from fastapi import APIRouter, HTTPException
from click import UUID
from typing import List

from app.db.models import ChatMessage, Chat
from app.chat.engine import create_new_chat, get_chat_history, generate_chat_response

chat_router = APIRouter()

@chat_router.post("/initiate/")
async def initiate(channel_id: str) -> str:
    """
    Asynchronously initiates a new chat with the specified channel ID.

    Args:
        channel_id (str): The ID of the channel for which the chat is initiated.

    Returns:
        dict: A dictionary containing the chat ID.
    """
    try:
        chat_id = await create_new_chat(channel_id)
        return str(chat_id)
    except Exception as e:
        HTTPException(status_code=500, detail="chat creation failed")

@chat_router.get("/history/")
async def chat_history(chat_id: str) -> List[ChatMessage]:
    """
    Retrieves the chat history for the specified chat ID.

    Args:
        chat_id (str): The ID of the chat to retrieve the history for.

    Returns:
        List[ChatMessage]: A list of ChatMessage objects representing the chat history.
    """
    try:
        chat_history = await get_chat_history(chat_id)
        return chat_history
    except Exception as e:
        raise HTTPException(status_code=500, detail="chat history retrieval failed")

@chat_router.post("/message/")
async def message(chat_id: str, user_message: str) -> List[ChatMessage]:
    """
    Saves the chat message to the database and generates a response.

    Args:
        chat_id (str): The ID of the chat.
        user_message (str): The chat message to save.
    
    Returns:
        List[ChatMessage]: The generated chat response.
    """
    try:
        # Get the chat from the database using the chat_id
        chat = await Chat.get(chat_id)
        
        # If chat is not found, raise a ValueError
        if not chat:
            logger.error(f"Chat not found for chat {chat_id}")
            raise HTTPException(status_code=400, detail=f"Chat not found for chat {chat_id}")

        chat_history = await generate_chat_response(chat, user_message)
        return chat_history
    except:
        raise HTTPException(status_code=500, detail="chat response generation failed")
