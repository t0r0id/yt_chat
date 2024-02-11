import logging
logger = logging.getLogger(__name__)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
import uvicorn
from uuid import uuid4

from app.db.db import init_db
from app.chat.router import chat_router
from app.onboarding.router import onboard_router
from app.db.models import User
from app.onboarding.engine import get_default_channels

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initilise DB
   await init_db()
   yield

#TODO: Add CORS Settings
app = FastAPI(
    title = "yt-chat",
    lifespan=lifespan
    ) 

class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
       # Check if a session ID is already present in the request headers
        session_id = None
        
        # If not, generate a new session ID
        if not request.cookies.get("sessionId"):
            session_id = str(uuid4())
            request.cookies.update({"sessionId": session_id})
            user = User(id=session_id)
            user.channels = [c.id for c in await get_default_channels()]
            await user.save()

        # Call the next middleware or the endpoint
        response = await call_next(request)

        # You can modify the response if needed
        # For example, you can set a cookie with the session ID
        if session_id:
            response.set_cookie(key="sessionId", value=session_id, max_age=3600*24*365)

        return response

# Register the middleware
app.add_middleware(SessionMiddleware)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
  
app.include_router(onboard_router, prefix="/onboard", tags=['onboard'])
app.include_router(chat_router, prefix="/chat", tags=['chat'])
def start():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == '__main__':
    start()