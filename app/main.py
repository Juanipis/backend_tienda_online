from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import psycopg2
from pydantic import BaseSettings
#Now we import the router from the auth.py file
from routers import auth, register

app = FastAPI()

#We add the router to the app with the prefix /auth and the tags
app.include_router(auth.router)
app.include_router(register.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}