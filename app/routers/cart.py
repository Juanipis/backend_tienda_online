from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Annotated, List
from app.routers.auth import get_current_active_user
from app.routers.user import User
from pymongo import MongoClient
from app.config import configuraciones

router = APIRouter()

async def connect_db():
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

class Product(BaseModel):
  product_id: int
  quantity: int

class Cart(BaseModel):
  user_id: int
  products: list[Product]
  

# Para obtener el carrito de un usuario
@router.post("/cart",response_model=Cart, tags=["cart"])
async def get_user_cart(current_user: Annotated[User, Depends(get_current_active_user)]):
  if not current_user:
    raise HTTPException(status_code=401, detail="Unauthorized")
  else:
    collection = await get_collection_db("test1", "carts")
    cart = collection.find_one({"user_id": current_user.id})
    return Cart(user_id=cart["user_id"],products=cart["products"])

# Para agregar un producto al carrito de un usuario
@router.post("/cart/add", tags=["cart"])
async def add_product_to_cart(current_user: Annotated[User, Depends(get_current_active_user)], products: List[Product]):
  """
  add_product_to_cart - Add a product to the cart of a user
  """
  #Si no hay usuario logueado, se devuelve un error
  if not current_user:
    raise HTTPException(status_code=401, detail="Unauthorized")
  else:
    #Se convierte la lista de productos a una lista de diccionarios
    products_dict = [product.dict() for product in products]  # Convertir a lista de diccionarios
    
    #Debemos comprobar que todos los productos existan en la base de datos y que la cantidad sea mayor a 0
    collection = await get_collection_db("test1", "products")
    for product in products_dict:
      product_id = product["product_id"]
      quantity = product["quantity"]
      prod = collection.find_one({"id": product_id})
      if not prod:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")
      if quantity <= 0:
        raise HTTPException(status_code=400, detail=f"Quantity for product with id {product_id} must be greater than 0")

    #Se obtiene el carrito del usuario
    collection = await get_collection_db("test1", "carts")
    cart = collection.find_one({"user_id": current_user.id})
    #Si el carrito ya existe, se actualiza, si no, se crea
    if cart:
      #Se actualiza el carrito con los nuevos productos
      collection.update_one({"user_id": current_user.id}, {"$push": {"products": {"$each": products_dict}}})
    else:
      #Se crea el carrito con los productos
      collection.insert_one({"user_id": current_user.id, "products": products_dict})
    return {"message": "Product added to cart successfully"}