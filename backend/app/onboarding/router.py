import logging
logger = logging.getLogger(__name__)

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Request, Body

from app.onboarding.engine import (create_onboarding_request,
                                   process_onboarding_request,
                                   search_for_channels,
                                   get_user_channels,
                                   get_channels
                                   )
from app.db.models import (Channel,
                           ChannelOnBoardingRequest,
                           ChannelOnBoardingRequestStatusEnum,
                           User
                           )

onboard_router = APIRouter()

@onboard_router.get("/search_channels/")
async def search_channels(query: str
                          , region: Optional[str]='US'
                          , limit: Optional[int]= 5) -> List[Channel]:
    """
    Endpoint to search for channel videos
    
    Args:
    - query: str, the search query
    - region: Optional[str], the region to search in
    - limit: Optional[int], the maximum number of results to return
    
    Returns:
    - List[Channel]: channel videos matching the search query
    """
    try:
        return await search_for_channels(query, region, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail="channel search failed")
    
@onboard_router.post("/channel_details/")
async def channel_details(request: Request,
                     channel_id: str = Body(..., embed=True)) -> Channel:
    """
    Retrieves the channel with the given channel_id if it is active.

    Args:
    - request: The incoming request
    - channel_id: The ID of the channel to retrieve

    Returns:
    - The channel with the given ID if it is active

    Raises:
    - HTTPException: If the channel is not found or not active
    """

    # Attempt to find the channel with the provided channel_id
    channels, _ = await get_channels([channel_id])

    # If the channel exists and is active, return it
    if channels:
        return channels[0]
    else:
        # If the channel is not found or not active, raise an HTTPException
        raise HTTPException(status_code=404, detail=f"Channel {channel_id} not found or not active")

@onboard_router.post("/user_channels")
async def user_channels(request: Request) -> List[Channel]:
    """
    Retrieves the added channels for the user session.

    Args:
        request (Request): The incoming request.

    Returns:
        List[Channel]: The list of top channels.
    """
    # Get the user session ID from the request cookies
    user_session_id = request.cookies.get('sessionId')

    # Return the list of channels
    return await get_user_channels(user_session_id)

@onboard_router.post("/remove_user_channel")
async def remove_user_channel(request: Request, channel_id: str = Body(..., embed=True)):
    """
    Removes the channel with the given ID from the user's list of channels.

    Args:
        request (Request): The incoming request.
        channel_id (str): The ID of the channel to remove.

    Returns:
        None
    """
    # Get the user session ID from the request cookies
    user_session_id = request.cookies.get('sessionId')
    # Remove the channel from the user's list of channels
    user = await User.get(user_session_id)
    if user and user.channels:
        user.channels.remove(channel_id)
        await user.save()
        return 
    else:
        return HTTPException(status_code=404, detail=f"User {user_session_id} not found")

@onboard_router.post("/initiate_request")
async def initiate_request(request: Request,
                           channel_id: str= Body(..., embed=True)) -> ChannelOnBoardingRequest:
    """
    An asynchronous function to handle the onboarding request for a specific channel.
    
    Parameters:
    - request: the incoming request object
    - channel_id: a string representing the ID of the channel
    - requested_by: a string representing the ID of the user who requested the onboarding
    
    Returns:
    - A dictionary containing the message, request_id, and channel_id
    """
    #TODO: Restrict access only to logged-in users
    # Get the user session ID from the request cookies
    user_session_id = request.cookies.get('sessionId')
    try:
        return await create_onboarding_request(channel_id, requested_by=user_session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail="request creation failed")

@onboard_router.post("/process_request")
async def process_request(request: Request,
                          request_id: str = Body(..., embed=True)) -> dict:
    """
    Process an onboarding request and returns a dictionary with a message and the request_id.

    Parameters:
    - request_id: a string representing the ID of the onboarding request

    Returns:
    - a dictionary with keys "message" and "request_id"
    """
    # TODO: Restrict access only to admins

    # Retrieve the onboarding request by ID
    onboarding_request = await ChannelOnBoardingRequest.get(request_id)

    # Check if the request exists
    if not onboarding_request:
        raise HTTPException(status_code=404, detail=f"Onboarding request ({request_id}) not found")

    # Check if the request is in the QUEUED state
    if onboarding_request.status != ChannelOnBoardingRequestStatusEnum.QUEUED:
        raise HTTPException(status_code=404, detail=f"Onboarding request ({onboarding_request.id}) is not in the QUEUED state. Request status: {onboarding_request.status}")

    # Check if the channel has already been onboarded
    existingRequest = await ChannelOnBoardingRequest.find_one(ChannelOnBoardingRequest.channel_id == onboarding_request.channel_id)
    if existingRequest and existingRequest.status == ChannelOnBoardingRequestStatusEnum.COMPLETED:
        onboarding_request.status = ChannelOnBoardingRequestStatusEnum.COMPLETED
        await onboarding_request.save()
        raise HTTPException(status_code=404, detail=f"Channel {onboarding_request.channel_id} for request {onboarding_request.id} has already been onboarded. Channel status: {channel.status}")

    try:
        await process_onboarding_request(onboarding_request)
        return {
            "message": f"Onboarding request successfully processed!",
            "request_id": request_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Request processing failed")
    