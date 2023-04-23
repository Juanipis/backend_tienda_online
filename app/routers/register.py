from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import re
import psycopg2
from random import randbytes
import hashlib
import smtplib 
from email.message import EmailMessage
from app.config import conexion, configuraciones
from typing import Annotated
from jose import jwt,jwe

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    telefono: str
    nombre: str
    person: bool
    apellido: str | None 

def create_register_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, configuraciones.secret_key, algorithm=configuraciones.algorithm)
    return encoded_jwt


def encrypt_register_token(token: str):
    encrypted = jwe.encrypt(token, configuraciones.jwe_key, algorithm='dir', encryption='A128GCM')
    return encrypted

def decrypt_register_token(token: str):
    try:
        decrypted = jwe.decrypt(token, configuraciones.jwe_key)
        return decrypted
    except:
        raise HTTPException(status_code=400, detail="Token invalido")


def get_password_hash(password):
    return pwd_context.hash(password)

def is_password_secure(password: str):
    return bool(re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$', password))



def send_verification_mail(reciver:str, email:EmailMessage):
    smtp = smtplib.SMTP_SSL("smtp.gmail.com")
    smtp.login(configuraciones.mail_sender, configuraciones.mail_password)
    smtp.sendmail(configuraciones.mail_sender, reciver, email.as_string())
    smtp.quit()

@router.post("/register", tags=["auth"])
async def registerPersona(form_data: Annotated[UserRegister, Depends()]):
    try:
        with conexion.cursor() as cursor:
            # Check if user already exists
            user_exist = cursor.execute(f"SELECT usuarioExiste('{form_data.email}')")
            if user_exist:
                raise HTTPException(status_code=400, detail="User already registered")

            # Check password security
            if not is_password_secure(form_data.password):
                raise HTTPException(status_code=400, detail="Password does not meet the security requirements")
            #Check if user is a person
            if form_data.person:
                if form_data.apellido == None:
                    raise HTTPException(status_code=400, detail="Apellido es requerido")
            # Create jwe token with user data and send it to user email
            # 1. Create expiration time for token
            access_token_expires = timedelta(minutes=configuraciones.register_expiration_time)
            # 2. Hash password
            form_data.password = get_password_hash(form_data.password)
            print(form_data)
            # 3. Create register token
            register_token = create_register_token(form_data.dict(), expires_delta=access_token_expires)
            #4. Encrypt register token
            encrypt_token = encrypt_register_token(register_token)
            #5. Send verification email
            email = EmailMessage()
            email["From"] = configuraciones.mail_sender
            email["To"] = form_data.email
            email["Subject"] = "Verificacion de cuenta"
            email.set_content(f"El link de verificacion de su cuenta: https://{configuraciones.api_url}:{configuraciones.api_port}/register/verify-email?token={encrypt_token.decode()}")
            send_verification_mail(form_data.email, email)
            return {"Usuario creado con exito, revise su correo para verificar su cuenta"}

    except psycopg2.Error as e:
        print("Ocurrió un error al conectar a PostgreSQL: ", e)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/register/verify-email", tags=["auth"])
async def verify_email(token: str):
    try:
        # 1. Decrypt token
        token_jwt = decrypt_register_token(token)
        # 2. Decode token
        userInfo = jwt.decode(token_jwt, configuraciones.secret_key, algorithms=[configuraciones.algorithm])
        # 3. Create user in database
        with conexion.cursor() as cursor:
            cursor.execute(f"SELECT insert_usuario('{userInfo['email']}', '{userInfo['nombre']}', '{userInfo['telefono']}', '{userInfo['password']}', true, '{userInfo['apellido']}', {userInfo['person']});")
            conexion.commit()
        return userInfo
    except psycopg2.Error as e:
        print("Ocurrió un error al conectar a PostgreSQL: ", e)
        raise HTTPException(status_code=500, detail="Error al actualizar usuario en la base de datos")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token invalido")