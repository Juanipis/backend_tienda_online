from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import psycopg2
from typing import Annotated
from app.config import conexion, configuraciones

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    access_token: str
    token_type: str
class TokenData(BaseModel):
    username: str | None = None
class User(BaseModel):
    email: str | None = None
    id: int | None = None
    enabled: bool | None = None
class UserInDB(User):
    hashed_password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(email: str):
    try:
        with conexion.cursor() as cursor:
            cursor.execute(f'select id,email,hashed_password,enabled from usuarios where email=\'{email}\';')
            email_db = cursor.fetchone()
            if(email_db != None):

                return UserInDB(id=email_db[0],email=email_db[1],hashed_password=email_db[2],enabled=email_db[3])
            else:
                return None
    except psycopg2.Error as e:
        print("Ocurrió un error al conectar a PostgreSQL: ", e)
    



def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or user.enabled == False:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, configuraciones.secret_key, algorithm=configuraciones.algorithm)
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
    access_token_expires = timedelta(minutes=configuraciones.acces_token_expire_minutes)
    access_token = create_access_token(
        data={"user_id": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}



#Functions to get active users

def get_user_by_id(user_id: int):
    try:
        with conexion.cursor() as cursor:
            cursor.execute(f'select id,enabled from usuarios where id={user_id};')
            user_fetched = cursor.fetchone()
            if(user_fetched != None):
                return User(id=user_fetched[0], enabled=user_fetched[1])
            else:
                return None
    except psycopg2.Error as e:
        print("Ocurrió un error al conectar a PostgreSQL: ", e)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, configuraciones.secret_key, algorithms=[configuraciones.algorithm])
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
    if current_user.enabled == False:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user