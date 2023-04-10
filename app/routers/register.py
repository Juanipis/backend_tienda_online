# -- ./routers/register.py --
from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import re
import random
import string
import psycopg2
from datetime import datetime, timedelta

from routers.auth import Settings, Token, create_access_token

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = Settings()


try:
    credenciales = {
        "dbname": settings.dbname,
        "user": settings.userdb,
        "password": settings.passworddb,
        "host": settings.hostdb,
        "port": settings.portdb
    }
    conexion = psycopg2.connect(**credenciales)
except psycopg2.Error as e:
    print("Ocurrió un error al conectar a PostgreSQL: ", e)

class User(BaseModel):
    email: EmailStr 
    password: str

class UserInDB(BaseModel):
    email: EmailStr
    hashed_password: str
    disabled: bool

def get_password_hash(password):
    return pwd_context.hash(password)

def is_password_secure(password: str):
    return bool(re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$', password))

def email_verification_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
  


@router.post("/register", response_model=Token, tags=["auth"])
async def register(user: User):
    try:
        with conexion.cursor() as cursor:
            # Check if user already exists
            cursor.execute(f"SELECT * FROM users WHERE email='{user.email}'")
            user_db = cursor.fetchone()
            if user_db is not None:
                raise HTTPException(status_code=400, detail="User already registered")

            # Check password security
            if not is_password_secure(user.password):
                raise HTTPException(status_code=400, detail="Password does not meet the security requirements")

            # Hash password and generate verification code
            hashed_password = get_password_hash(user.password)
            verification_code = email_verification_code()

            # Add user to database
            cursor.execute(f"SELECT insert_user('{user.email}, '{hashed_password}', '{verification_code}', false);")
            conexion.commit()
            # Send email with verification link
            # code here
            
            print(f"Verification code: {verification_code}")

            # Create access token
            access_token_expires = timedelta(minutes=settings.acces_token_expire_minutes)
            access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)

            return {"access_token": access_token, "token_type": "bearer"}

    except psycopg2.Error as e:
        print("Ocurrió un error al conectar a PostgreSQL: ", e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/verify-email")
async def verify_email(token: str):
    # Decodificamos el token
    try:
        payload = JWTError.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise JWTError
    except JWTError:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")

    # Buscamos al usuario en la base de datos
    try:
        with conexion.cursor() as cursor:
            cursor.execute(f"SELECT email FROM users WHERE email='{email}'")
            email = cursor.fetchone()[0]
            cursor.execute(f"UPDATE users SET disabled=false WHERE email={email}")
            conexion.commit()
            return {"message": "Email verificado correctamente"}
    except psycopg2.Error as e:
        print("Ocurrió un error al conectar a PostgreSQL: ", e)
        raise HTTPException(status_code=500, detail="Error al actualizar usuario en la base de datos")