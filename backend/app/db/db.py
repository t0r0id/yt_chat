import os
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from app.db.models import Channel, ChannelOnBoardingRequest, Chat, ActiveChatSessionMap, User

class MongoDBClientSingleton:
    __instance = None

    @staticmethod
    def get_instance():
        if MongoDBClientSingleton.__instance is None:
            MongoDBClientSingleton()
        return MongoDBClientSingleton.__instance
    
    def __init__(self) -> None:
        if MongoDBClientSingleton.__instance is not None:
            raise Exception("Only one instance of MongoDbClientSingleton is allowed")
        else:
            db_uri =  os.environ['MONGO_URI']
            self.async_client = AsyncIOMotorClient(db_uri)
            MongoDBClientSingleton.__instance = self

async def init_db():
    mongo_client = MongoDBClientSingleton.get_instance().async_client
    await init_beanie(database=mongo_client[os.environ['DB_NAME']], document_models=[
        ChannelOnBoardingRequest,
        Channel,
        Chat,
        ActiveChatSessionMap,
        User
        ])
