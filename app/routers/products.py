from fastapi import APIRouter, Query
from typing import Optional, List
from app.config import Configuraciones
from app.models import ProductInfo
from app.mongodb import get_collection_db

router = APIRouter()


@router.get("/search_product", response_model=List[ProductInfo], tags=["info_product"])
async def search_product(name: Optional[str] = None, categories: Optional[List[int]] = Query(None), product_id: Optional[int] = None):
  collection = await get_collection_db(Configuraciones.MONGODB_NAME, Configuraciones.MONGODB_COLLECTION_PRODUCT)
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