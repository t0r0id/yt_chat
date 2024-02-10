import logging
logger = logging.getLogger(__name__)

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Request, Body

from app.onboarding.engine import create_onboarding_request, process_onboarding_request, search_for_channels, get_top_channels
from app.db.models import Channel, ChannelOnBoardingRequest, ChannelOnBoardingRequestStatusEnum

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
    
@onboard_router.post("/channel")
async def get_channel(request: Request,
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
    channel = await Channel.find_one(Channel.id == channel_id)

    # If the channel exists and is active, return it
    if channel:
        return channel
    else:
        # If the channel is not found or not active, raise an HTTPException
        raise HTTPException(status_code=404, detail=f"Channel {channel_id} not found or not active")

@onboard_router.post("/channels")
async def get_channels(request: Request, limit: int = 5) -> List[Channel]:
    """
    Retrieves the top channels for the user session.

    Args:
        request (Request): The incoming request.
        limit (int, optional): The maximum number of channels to retrieve. Defaults to 5.

    Returns:
        List[Channel]: The list of top channels.
    """
    user_session_id = request.cookies.get('sessionId')
    channels = await get_top_channels(user_session_id, limit)

    return channels

@onboard_router.post("/initiate_request")
async def initiate_request(request: Request,
                           channel_id: str= Body(..., embed=True),
                           requested_by: str= Body(..., embed=True)) -> ChannelOnBoardingRequest:
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
    try:
        return await create_onboarding_request(channel_id, requested_by)
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
    channel = await Channel.find_one(Channel.id == onboarding_request.channel_id)
    if channel:
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
    
    
    