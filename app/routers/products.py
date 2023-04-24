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
  try:
    return MongoClient(configuraciones.mongodb_url)
  except Exception as e:
    raise HTTPException(status_code=500, detail="Error connecting to the database")



router = APIRouter()

async def get_product_info_db(product_id:int):
  dbname = "test1"
  collection_name = "products"
  client = await connect_db()
  db = client[dbname]
  collection = db[collection_name]
  product = collection.find_one({"id":product_id})
  if product:
    return ProductInfo(id=product["id"],name=product["name"],categories=product["categories"],description=product["description"],image_url=product["image_url"],price_gr=product["price_gr"])
  else:
    raise HTTPException(status_code=404, detail="Product not found")
  
@router.get("/info_product_id",response_model=ProductInfo, tags=["info_product"])
async def get_info_product(product_id: int):
  return await get_product_info_db(product_id)


@router.get("/search_product", response_model=List[ProductInfo], tags=["info_product"])
async def search_product_by_name_and_category(name: Optional[str] = None, categories: Optional[List[int]] = Query(None)):
    dbname = "test1"
    collection_name = "products"
    client = await connect_db()
    db = client[dbname]
    collection = db[collection_name]
    query = {}
    if name:
        query["name"] = {"$regex": f".*{name}.*", "$options": "i"}
    if categories:
        query["categories"] = {"$in": categories}
    products = collection.find(query)
    return [ProductInfo(id=product["id"],name=product["name"],categories=product["categories"],description=product["description"],image_url=product["image_url"],price_gr=product["price_gr"]) for product in products]