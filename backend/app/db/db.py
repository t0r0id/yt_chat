from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.db.models import Channel, Video, ChannelOnBoardingRequest
from dotenv import load_dotenv
import os
load_dotenv()


async def init_db():
    db_uri =  os.environ['MONGODB_URI']
    client = AsyncIOMotorClient(db_uri)
    await init_beanie(database=client.db_name, document_models=[
        ChannelOnBoardingRequest,
        Channel,
        Video
        ])
    
