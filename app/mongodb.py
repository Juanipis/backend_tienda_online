from pymongo import MongoClient
from fastapi import HTTPException
from app.config import Configuraciones

async def connect_db():
  """
  connect_db - Connect to the database
  """
  try:
    return MongoClient(Configuraciones.mongodb_url)
  except Exception as e:
    raise HTTPException(status_code=500, detail="Error connecting to the database")

async def get_collection_db(dbname: str, collection_name: str):
  """
  get_collection_db - Connect to the database and return the collection
  """
  try:
    client = await connect_db()
    db = client[dbname]
    collection = db[collection_name]
    return collection
  except Exception as e:
    raise HTTPException(status_code=500, detail="Error connecting to the database")