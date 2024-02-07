import logging
logger = logging.getLogger(__name__)

from typing import Optional, List
from fastapi import APIRouter, HTTPException
from click import UUID 

from app.onboarding.engine import create_onboarding_request, process_onboarding_request, search_for_channels
from app.db.models import Channel, ChannelOnBoardingRequest, ChannelOnBoardingRequestStatusEnum

onboard_router = APIRouter()

@onboard_router.get("/search_channels/")
async def search_channels(query: str, region: Optional[str]='US', limit: Optional[int]=5) -> List[Channel]:
    """
    Endpoint to search for channel videos
    
    Args:
    - query: str, the search query
    - region: Optional[str], the region to search in
    - limit: Optional[int], the maximum number of results to return
    
    Returns:
    - dict: channel videos matching the search query
    """
    try:
        return await search_for_channels(query, region, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail="channel search failed")

@onboard_router.post("/initiate_request")
async def initiate_request(channel_id: str, requested_by: str) -> ChannelOnBoardingRequest:
    """
    An asynchronous function to handle the onboarding request for a specific channel.
    
    Parameters:
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
async def process_request(request_id: str) -> dict:
    """
    A function to process an onboarding request identified by the request_id parameter and returns a dictionary with a message and the request_id.
    
    Parameters:
    - request_id: a string representing the ID of the onboarding request
    
    Returns:
    - a dictionary with keys "message" and "request_id"
    """
    #TODO: Restrict access only to admins

    # Retrieve the onboarding request by ID
    request = await ChannelOnBoardingRequest.get(request_id)

    # Check if the request exists
    if not request:
        raise HTTPException(status_code=404, detail=f"Onboarding request ({request_id}) not found")

    # Check if the request is in the QUEUED state
    if request.status != ChannelOnBoardingRequestStatusEnum.QUEUED:
        raise HTTPException(status_code=404, detail=f"Onboarding request ({request.id}) is not in the QUEUED state. Request status: {request.status}")

    # Check if the channel has already been onboarded
    channel = Channel.find_one(Channel.id == request.channel_id)
    if await channel:
        request.status = ChannelOnBoardingRequestStatusEnum.COMPLETED
        await request.save()
        raise HTTPException(status_code=404
                            , detail=f"Channel {request.channel_id} for request {request.id} has already been onboarded. Channel status: {channel.status}"
                            )
    try:
        await process_onboarding_request(request)
        return {
            "message": f"Onboarding request successfully processed!",
            "request_id": request_id
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail="request processing failed")
    