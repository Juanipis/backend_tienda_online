# Library for creating and managing API routes
from fastapi import APIRouter, Depends, HTTPException, Query
# Library for defining annotated types and lists
from typing import Annotated, List
# Local module for configuring the environment variables
from app.config import Configuraciones
# Local module for getting the current active user from the authentication
from app.routers.auth import get_current_active_user
# Local module for defining the data model of the user
from app.routers.user import User
# Local module for getting the MongoDB collection from the database
from app.mongodb import get_collection_db
# Local module for defining the data models of the cart and the product list
from app.models import Cart, ProductList


router = APIRouter()

# To get the cart of a user
@router.get("/cart",response_model=Cart, tags=["cart"])
async def get_user_cart(current_user: Annotated[User, Depends(get_current_active_user)]):
  """
  get_user_cart - Get the cart of a user
  """
  if not current_user:
    raise HTTPException(status_code=401, detail="Unauthorized")
  else:
    collection = await get_collection_db(Configuraciones.MONGODB_NAME, Configuraciones.MONGODB_COLLECTION_CART)
    cart = collection.find_one({"user_id": current_user.id})
    return Cart(user_id=cart["user_id"],products=cart["products"])

# To add a product to the cart of a user
@router.post("/cart/add", tags=["cart"])
async def add_product_to_cart(current_user: Annotated[User, Depends(get_current_active_user)], products: ProductList):
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
    collection = await get_collection_db(Configuraciones.MONGODB_NAME, Configuraciones.MONGODB_COLLECTION_PRODUCT)
    for product in products_dict:
      product_id = product["product_id"]
      quantity = product["quantity"]
      prod = collection.find_one({"id": product_id})
      if not prod:
        raise HTTPException(status_code=404, detail=f"Product with id {product_id} not found")
      if quantity <= 0:
        raise HTTPException(status_code=400, detail=f"Quantity for product with id {product_id} must be greater than 0")

    #Get the cart of the user
    collection = await get_collection_db(Configuraciones.MONGODB_NAME, Configuraciones.MONGODB_COLLECTION_CART)
    cart = collection.find_one({"user_id": current_user.id})
    #Check if the user has a cart, if not, create one
    if cart:
      #Check if the product is already in the cart, if so, update the quantity
      collection.update_one({"user_id": current_user.id}, {"$push": {"products": {"$each": products_dict}}})
    else:
      #Create the cart
      collection.insert_one({"user_id": current_user.id, "products": products_dict})
    return {"message": "Product added to cart successfully"}

# To delete a product from the cart of a user
@router.delete("/cart/delete", tags=["cart"])
async def delete_product_from_cart(current_user: Annotated[User, Depends(get_current_active_user)], products_cart_id: List[int]):
  """
  delete_product_from_cart - Delete a product from the cart of a user
  """
  #If the user is not logged in, raise an exception
  if not current_user:
    raise HTTPException(status_code=401, detail="Unauthorized")
  else:
    #Get the cart of the user
    collection = await get_collection_db(Configuraciones.MONGODB_NAME, Configuraciones.MONGODB_COLLECTION_CART)
    cart = collection.find_one({"user_id": current_user.id})
    #Check if the user has a cart, if not, raise an exception
    if cart:
      #Check if the products are in the cart, if so, delete them
      for product_cart_id in products_cart_id:
        collection.update_one({"user_id": current_user.id}, {"$pull": {"products": {"product_id": product_cart_id}}})
      return {"message": "Product deleted from cart successfully"}
    else:
      raise HTTPException(status_code=404, detail="Cart not found")