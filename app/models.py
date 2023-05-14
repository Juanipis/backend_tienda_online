
from pydantic import BaseModel, EmailStr
from typing import List
"""
  Models - Models for the API
  - They are used to validate the data that is sent to the API and to return the data in the responses
  - They are used in the routers
  - They are used in the database
  - They are created with Pydantic
  - They are used in the API documentation
  - They are used in the tests
"""
# -------------------------------
"""
  Models for manage users and auth
"""
class UserInfo(BaseModel):
  """
  UserInfo - User info model
  """
  email: str
  nombre: str
  telefono: str
  is_persona: bool
  enabled: bool
  apellido: str = None
  
class User(BaseModel):
  """
  User - User model
  """
  email: str | None = None
  id: int | None = None
  enabled: bool | None = None
    

class UserRegister(BaseModel):
  """
  UserRegister - User register model
  """
  email: EmailStr
  password: str
  telefono: str
  nombre: str
  person: bool
  apellido: str | None 

# For login
class Token(BaseModel):
  """
  Token - Token model
  """
  access_token: str
  token_type: str

class TokenData(BaseModel):
  """
  TokenData - Token data model
  """
  username: str | None = None
class User(BaseModel):
  """
  User - User model
  """
  email: str | None = None
  id: int | None = None
  enabled: bool | None = None

class UserInDB(User):
  """
  UserInDB - User in DB model
  """
  hashed_password: str


# -------------------------------

"""
  Models for manage products
"""

class Product(BaseModel):
  """
  Product - Product model
  """
  product_id: int
  quantity: int

class ProductList(BaseModel):
  """
  ProductList - Product list model
  """
  products: List[Product]

class ProductInfo(BaseModel):
  """
  ProductInfo - Product info model
  """
  id: int
  name: str
  categories: list
  description: str
  image_url: str | None
  price_gr: float

class Cart(BaseModel):
  """
  Cart - Cart model
  """
  user_id: int
  products: list[Product]