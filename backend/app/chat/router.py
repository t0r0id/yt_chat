import logging
logger = logging.getLogger(__name__)

from fastapi import APIRouter, HTTPException, Request, Body
from click import UUID
from typing import Generator, List
from sse_starlette.sse import EventSourceResponse
from llama_index.core.llms.types import MessageRole

from app.db.models import ChatResponse, Chat, ChatResponseStatusEnum
from app.chat.engine import create_new_chat, get_chat_history, generate_chat_response_stream

chat_router = APIRouter()

@chat_router.post("/initiate/")
async def initiate(request: Request, channel_id: str = Body(..., embed=True)) -> str:
    """
    Asynchronously initiates a new chat with the specified channel ID.

    Args:
        request (Request): The incoming request object.
        channel_id (str): The ID of the channel for which the chat is initiated.

    Returns:
        str: A string containing the chat ID.
    """
    #TODO: Add user authentication
    try:
        # Create a new chat with the specified channel ID
        chat_id = await create_new_chat(channel_id)
        return str(chat_id)
    except Exception as e:
        # If chat creation fails, raise an HTTPException
        raise HTTPException(status_code=500, detail="chat creation failed")


@chat_router.post("/history/")
async def chat_history(request: Request, chat_id: str = Body(..., embed=True)) -> List[ChatResponse]:
    """
    Retrieves the chat history for the specified chat ID.

    Args:
        request (Request): The incoming request object.
        chat_id (str): The ID of the chat to retrieve the history for.

    Returns:
        List[ChatMessage]: A list of ChatMessage objects representing the chat history.
    """
    #TODO: Add user authentication
    try:
        # Retrieve chat history
        chat_history = await get_chat_history(chat_id)
        return chat_history
    except Exception as e:
        # Raise exception if chat history retrieval fails
        raise HTTPException(status_code=500, detail="chat history retrieval failed")
    
@chat_router.post("/message_stream/")
async def message_stream(request: Request,
                         chat_id: str = Body(..., embed=True),
                         user_message: str = Body(..., embed=True)) -> EventSourceResponse:
    """
    Endpoint for streaming chat responses.

    Args:
        request (Request): The incoming request object.
        chat_id (str): The ID of the chat.
        user_message (str): The message from the user.

    Returns:
        EventSourceResponse: The response stream.
    """
    try:
        # Get the chat by ID
        chat = await Chat.get(chat_id)

        # If chat not found, raise an error
        if not chat:
            logger.error(f"Chat not found for chat {chat_id}")
            raise HTTPException(status_code=400, detail=f"Chat not found for chat {chat_id}")
        
        # Generate the chat response stream
        stream = await generate_chat_response_stream(chat, user_message)
        
        # If stream not generated, add failed response to chat history and raise an error
        if not stream:
            chat.chat_history.append(ChatResponse(role=MessageRole.USER
                                                  , content=user_message
                                                  , status=ChatResponseStatusEnum.FAILED
                                                  , error="No stream generated"
                                                  ))
            await chat.save()
            raise HTTPException(status_code=500, detail="chat response stream generation failed")
        
        # Initialize the chat response
        chat_response = ChatResponse(role=MessageRole.ASSISTANT, content="", status=ChatResponseStatusEnum.IN_PROGRESS)
        
        # Define the stream response generator
        async def stream_response_generator(chat) -> Generator[ChatResponse, None, None]:
            """
            Generator for streaming chat responses.

            Args:
                chat (Chat): The chat object.

            Yields:
                ChatResponse: The chat response.

            Raises:
                HTTPException: If chat response generation failed.
            """
            async for delta in stream.async_response_gen():
                chat_response.content += delta
                yield chat_response
            chat_response.status = ChatResponseStatusEnum.COMPLETED
            chat.chat_history.append(ChatResponse(role=MessageRole.USER,
                                                  content=user_message,
                                                  status=ChatResponseStatusEnum.COMPLETED
                                                  )
                                                  )
            chat.chat_history.append(chat_response)
            chat = await chat.save()
            yield chat_response
        return EventSourceResponse(stream_response_generator(chat))
    except Exception as e:
        logger.error(f"Failed to generate chat response stream for chat {chat_id}", e)
        chat.chat_history.append(ChatResponse(role=MessageRole.USER
                                                  , content=user_message
                                                  , status=ChatResponseStatusEnum.FAILED
                                                  , error="exception raised"
                                                  ))
        await chat.save()
        raise HTTPException(status_code=500, detail="chat response generation failed")

@chat_router.post("/message/")
async def message(request: Request,
                  chat_id: str= Body(..., embed=True),
                  user_message: str= Body(..., embed=True)) -> ChatResponse:
    """
    Endpoint to handle incoming chat messages and generate a response without stream.

    Args:
    - request (Request): The incoming request object.
    - chat_id (str): The ID of the chat session.
    - user_message (str): The message sent by the user.

    Returns:
    - ChatResponse: The response generated for the user message.
    """
    try:
        # Get the response from the message stream
        response: EventSourceResponse = await message_stream(request, chat_id, user_message)
        final_message = None
        # Iterate through the response body to get the final message
        async for message in response.body_iterator:
            final_message = message
        # Return the final message if it's not None, otherwise raise an exception
        if final_message is not None:
            return final_message
        else:
            raise HTTPException(status_code=500, detail="chat response generation failed")
    except:
        raise HTTPException(status_code=500, detail="chat response generation failed")
