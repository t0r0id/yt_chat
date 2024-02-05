from app.db.models import Channel, ChannelStatus
from fastapi import FastAPI
from app.db.db import MongoDBClientSingleton, init_db
from contextlib import asynccontextmanager
from llama_index import VectorStoreIndex
import uvicorn
from app.onboarding.engine import process_onboarding_request, create_onboarding_request
from llama_index.vector_stores.pinecone import PineconeVectorStore
import os

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
    await process_onboarding_request(request_id)
    return {
       "message": f"Onboarding request successfully processed!",
       "request_id": request_id
    }

@app.post("/query")
async def query(query: str, channel_id: str) -> dict:
   """
   Asynchronous function for querying a channel with the provided query and channel_id.

   Args:
       query (str): The query string for the search.
       channel_id (str): The ID of the channel to be queried.

   Returns:
       dict: A dictionary containing the response from the query.
   """
   #TODO: Add error handling 
   # Find the channel based on the provided channel_id
   channel = await Channel.find_one(Channel.id == channel_id)

   # Check if the channel is not found or not active
   if not channel or not channel.status == ChannelStatus.ACTIVE:
       return {"message": "Channel not found"}

   # Get the MongoDB client instance
   mongo_client = MongoDBClientSingleton.get_instance().sync_client

   # Create an instance of MongoDBAtlasVectorSearch
   vector_store = PineconeVectorStore(api_key=os.environ['PINECONE_API_KEY'],
                                     index_name=os.environ['VECTOR_STORE_INDEX_NAME'],
                                     namespace=channel.id
                                     )

   # Create an index from the vector store
   index = VectorStoreIndex.from_vector_store(vector_store)

   # Create a query engine from the index
   query_engine = index.as_query_engine()

   # Query the channel and get the response
   response = query_engine.query(query)

   # Return the response in a dictionary
   return {"response": response.response}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)