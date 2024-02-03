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


app = FastAPI(lifespan=lifespan)   
@app.get("/") 
async def main_route():     
  return {"message": "Hello World"}


@app.post("/request_onboarding")
async def request_onboarding(channel_id: str) -> dict:
    request_id = await create_onboarding_request(channel_id, None)
    return {
       "message": f"Onboarding request successfully created!\n{request_id} \n {channel_id}"
            }


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)