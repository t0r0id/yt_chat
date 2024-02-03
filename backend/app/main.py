from fastapi import FastAPI
from app.db.db import init_db
from contextlib import asynccontextmanager
import uvicorn
from app.scripts.channel_onboarding import process_onboarding_request, create_onboarding_request

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initilise DB
   await init_db()
   yield

#TODO: Add CORS Settings
app = FastAPI(lifespan=lifespan)   
@app.get("/") 
async def main_route():     
  return {"message": "Hello World"}


@app.post("/request_onboarding")
async def request_onboarding(channel_id: str, requested_by: str) -> dict:
    """
    An asynchronous function to handle the onboarding request for a specific channel.
    
    Parameters:
    - channel_id: a string representing the ID of the channel
    - requested_by: a string representing the ID of the user who requested the onboarding
    
    Returns:
    - A dictionary containing the message, request_id, and channel_id
    """
    #TODO: Add error handling
    #TODO: Restrict access only to logged-in users
    request_id = await create_onboarding_request(channel_id, requested_by)
    return {
       "message": f"Onboarding request successfully created!",
       "request_id": str(request_id),
       "channel_id": channel_id
            }

@app.post("/process_onboarding_request")
async def onboard_request(request_id: str) -> dict:
    """
    A function to process an onboarding request identified by the request_id parameter and returns a dictionary with a message and the request_id.
    
    Parameters:
    - request_id: a string representing the ID of the onboarding request
    
    Returns:
    - a dictionary with keys "message" and "request_id"
    """
    #TODO: Add error handling
    #TODO: Restrict access only to admins
    success = await process_onboarding_request(request_id)
    return {
       "message": f"Onboarding request successfully processed!",
       "request_id": request_id
    }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)