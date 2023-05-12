from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Annotated, Optional, List
from pymongo import MongoClient
from app.config import configuraciones

class ProductInfo(BaseModel):
  id: int
  name: str
  categories: list
  description: str
  image_url: str | None
  price_gr: float


async def connect_db():
  """
  connect_db - Connect to the database
  """
  try:
    return MongoClient(configuraciones.mongodb_url)
  except Exception as e:
    raise HTTPException(status_code=500, detail="Error connecting to the database")

async def get_collection_db(dbname: str, collection_name: str):
  try:
    client = await connect_db()
    db = client[dbname]
    collection = db[collection_name]
    return collection
  except Exception as e:
    raise HTTPException(status_code=500, detail="Error connecting to the database")

router = APIRouter()


@router.get("/search_product", response_model=List[ProductInfo], tags=["info_product"])
async def search_product(name: Optional[str] = None, categories: Optional[List[int]] = Query(None), product_id: Optional[int] = None):
  collection = await get_collection_db("test1", "products")
  products = []
  if product_id:
      products = collection.find({"id": product_id})
  else:
    query = {}
    if name:
        query["name"] = {"$regex": f".*{name}.*", "$options": "i"}
    if categories:
        query["categories"] = {"$in": categories}
    products = collection.find(query)
  return [ProductInfo(id=product["id"],name=product["name"],categories=product["categories"],description=product["description"],image_url=product["image_url"],price_gr=product["price_gr"]) for product in products]