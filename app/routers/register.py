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
from random import randbytes
import hashlib
import smtplib 
from email.message import EmailMessage

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




@router.post("/register", tags=["auth"])
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
            token = randbytes(10)
            hashedCode = hashlib.sha256()
            hashedCode.update(token)
            verification_code = hashedCode.hexdigest()
            # Add user to database
            cursor.execute(f"SELECT insert_user('{user.email}','{hashed_password}',true,'{verification_code}');")
            conexion.commit()
            
            # Send verification email
            email = EmailMessage()
            email["From"] = settings.mail_sender
            email["To"] = user.email
            email["Subject"] = "Verificacion de cuenta"
            email.set_content(f"El link de verificacion de su cuenta:localhost:8000/verify-email?token={verification_code}")
            smtp = smtplib.SMTP_SSL("smtp.gmail.com")
            smtp.login(settings.mail_sender, settings.mail_password)
            smtp.sendmail(settings.mail_sender, user.email, email.as_string())
            smtp.quit()
            return {"Usuario creado con exito, revise su correo para verificar su cuenta"}

    except psycopg2.Error as e:
        print("Ocurrió un error al conectar a PostgreSQL: ", e)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/verify-email")
async def verify_email(token: str):
    # Buscamos al usuario en la base de datos
    try:
        with conexion.cursor() as cursor:
            cursor.execute(f"SELECT verificarTokenRegistro('{token}')")
            verify = cursor.fetchone()[0]
            conexion.commit()
            if verify:
                cursor.execute(f"SELECT activarusuario('{token}')")
                return {"message": "Usuario verificado correctamente"}
            else:
                raise HTTPException(status_code=401, detail="Codigo de verificacion incorrecto o vencido")
    except psycopg2.Error as e:
        print("Ocurrió un error al conectar a PostgreSQL: ", e)
        raise HTTPException(status_code=500, detail="Error al actualizar usuario en la base de datos")