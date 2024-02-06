import logging
logger = logging.getLogger(__name__)

from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from app.db.db import init_db
from app.chat.router import chat_router
from app.onboarding.router import onboard_router

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
  
app.include_router(onboard_router, prefix="/onboard", tags=['onboard'])
app.include_router(chat_router, prefix="/chat", tags=['chat'])
def start():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == '__main__':
    start()