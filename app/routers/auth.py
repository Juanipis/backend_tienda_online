# Library for working with dates and times
from datetime import datetime, timedelta
# Library for validating email addresses
from email_validator import validate_email
# Library for connecting and executing queries with PostgreSQL
import psycopg2
# Local modules for configuring the database connection and the environment variables
from app.config import ConexionPostgres, Configuraciones
# Library for defining annotated types
from typing import Annotated
# Local modules for defining the data models of the application
from app.models import Token, TokenData, User, UserInDB
# Library for encrypting and verifying passwords
from passlib.context import CryptContext
# Library for encoding and decoding JWT tokens
from jose import JWTError, jwt
# Library for creating and managing API routes
from fastapi import APIRouter, Depends, HTTPException, status
# Library for implementing authentication with OAuth2
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
  """
  verify_password - Verify the password
  """
  return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
  """
	get_password_hash - Get the password hash
  """
  return pwd_context.hash(password)

def get_user(email: str):
  """
	get_user - Get the user from the database
  """
  try:
    with ConexionPostgres.cursor() as cursor:
      cursor.execute(f'select id,email,hashed_password,enabled from usuarios where email=\'{email}\';')
      email_db = cursor.fetchone()
      if(email_db != None):
        return UserInDB(id=email_db[0],email=email_db[1],hashed_password=email_db[2],enabled=email_db[3])
      else:
        return None
  except psycopg2.Error as e:
    print("Ocurrió un error al conectar a PostgreSQL: ", e)



def authenticate_user(username: str, password: str):
  """
	authenticate_user - Authenticate the user
  """
  try:
    #First validate the email has the correct format
    email_valid = validate_email(username)
    #Then get the user from the database
    user = get_user(email_valid.normalized)
    #If the user does not exist or is not enabled, return False
    if not user or user.enabled == False:
      return False
    #If the password is not correct, return False
    if not verify_password(password, user.hashed_password):
      return False
    #If everything is correct, return the user
    return user
  except:
    return False


def create_access_token(data: dict, expires_delta: timedelta | None = None):
  """
	create_access_token - Create the access token
  """
  to_encode = data.copy()
  if expires_delta:
    expire = datetime.utcnow() + expires_delta
  else:
    expire = datetime.utcnow() + timedelta(minutes=15)
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, Configuraciones.SECRET_KEY, algorithm=Configuraciones.ALGORITHM)
  return encoded_jwt




#We add the router to the app with the prefix /auth and the tags
@router.post("/token", response_model=Token,tags=["auth"])
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
  user = authenticate_user(form_data.username, form_data.password) #On oauth2 the username is the email
  
  if not user:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Incorrect username or password",
      headers={"WWW-Authenticate": "Bearer"},
    )
  access_token_expires = timedelta(minutes=Configuraciones.ACCESS_TOKEN_EXPIRATION_TIME)
  access_token = create_access_token(
    data={"user_id": user.id}, expires_delta=access_token_expires
  )
  return {"access_token": access_token, "token_type": "bearer"}



#Functions to get active users

def get_user_by_id(user_id: int):
  """
	get_user_by_id - Get the user by id
  """
  try:
    with ConexionPostgres.cursor() as cursor:
      cursor.execute(f'select id,enabled from usuarios where id={user_id};')
      user_fetched = cursor.fetchone()
      if(user_fetched != None):
        return User(id=user_fetched[0], enabled=user_fetched[1])
      else:
        return None
  except psycopg2.Error as e:
    print("Ocurrió un error al conectar a PostgreSQL: ", e)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
  """
	get_current_user - Get the current user
  """
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
  )
  try:
    payload = jwt.decode(token, Configuraciones.SECRET_KEY, algorithms=[Configuraciones.ALGORITHM])
    user_id: str = payload.get("user_id")
    if user_id is None:
      raise credentials_exception
    token_data = TokenData(username=user_id)
  except JWTError:
    raise credentials_exception
  user = get_user_by_id(user_id=token_data.username)
  if user is None:
    raise credentials_exception
  return user

async def get_current_active_user( current_user: Annotated[User, Depends(get_current_user)]):
  """
	get_current_active_user - Get the current active user 
  """
  if current_user.enabled == False:
    raise HTTPException(status_code=400, detail="Inactive user")
  return current_user