from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated, List
from app.routers.auth import get_current_active_user
from app.routers.user import User
from app.mongodb import get_collection_db
from app.config import Configuraciones
from app.models import Product, Cart
router = APIRouter()



# To get the cart of a user
@router.post("/cart",response_model=Cart, tags=["cart"])
async def get_user_cart(current_user: Annotated[User, Depends(get_current_active_user)]):
  """
  get_user_cart - Get the cart of a user
  """
  if not current_user:
    raise HTTPException(status_code=401, detail="Unauthorized")
  else:
    collection = await get_collection_db(Configuraciones.mongodb_name, Configuraciones.mongodb_collection_cart)
    cart = collection.find_one({"user_id": current_user.id})
    return Cart(user_id=cart["user_id"],products=cart["products"])

# To add a product to the cart of a user
@router.post("/cart/add", tags=["cart"])
async def add_product_to_cart(current_user: Annotated[User, Depends(get_current_active_user)], products: List[Product]):
  """
  add_product_to_cart - Add a product to the cart of a user
  """
  #If the user is not logged in, raise an exception
  if not current_user:
    raise HTTPException(status_code=401, detail="Unauthorized")
  else:
    #Convert the list of products to a list of dictionaries
    products_dict = [product.dict() for product in products]  # Convertir a lista de diccionarios
    
    #Check if the products exist and if the quantity is greater than 0
    collection = await get_collection_db(Configuraciones.mongodb_name, Configuraciones.mongodb_collection)
    for product in products_dict:
      product_id = product["product_id"]
      quantity = product["quantity"]
      prod = collection.find_one({"id": product_id})
      if not prod:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")
      if quantity <= 0:
        raise HTTPException(status_code=400, detail=f"Quantity for product with id {product_id} must be greater than 0")

    #Get the cart of the user
    collection = await get_collection_db(Configuraciones.mongodb_name, Configuraciones.mongodb_collection_cart)
    cart = collection.find_one({"user_id": current_user.id})
    #Check if the user has a cart, if not, create one
    if cart:
      #Check if the product is already in the cart, if so, update the quantity
      collection.update_one({"user_id": current_user.id}, {"$push": {"products": {"$each": products_dict}}})
    else:
      #Create the cart
      collection.insert_one({"user_id": current_user.id, "products": products_dict})
    return {"message": "Product added to cart successfully"}