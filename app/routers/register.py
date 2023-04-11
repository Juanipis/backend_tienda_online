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

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(BaseModel):
    email: EmailStr 
    password: str
    
class Persona(BaseModel):
    email: EmailStr
    password: str
    telefono: str
    nombre: str
    apellido: str
class Empresa(BaseModel):
    email: EmailStr
    password: str
    telefono: str
    nombre: str

def get_password_hash(password):
    return pwd_context.hash(password)

def is_password_secure(password: str):
    return bool(re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$', password))

def get_verification_code():
    token = randbytes(10)
    hashedCode = hashlib.sha256()
    hashedCode.update(token)
    verification_code = hashedCode.hexdigest()
    return verification_code

def send_verification_mail(reciver:str, email:EmailMessage):
    smtp = smtplib.SMTP_SSL("smtp.gmail.com")
    smtp.login(configuraciones.mail_sender, configuraciones.mail_password)
    smtp.sendmail(configuraciones.mail_sender, reciver, email.as_string())
    smtp.quit()

@router.post("/register/persona", tags=["auth"])
async def registerPersona(form_data: Annotated[Persona, Depends()]):
    try:
        with conexion.cursor() as cursor:
            # Check if user already exists
            user_exist = cursor.execute(f"SELECT usuarioExiste('{form_data.email}')")
            if user_exist:
                raise HTTPException(status_code=400, detail="User already registered")

            # Check password security
            if not is_password_secure(form_data.password):
                raise HTTPException(status_code=400, detail="Password does not meet the security requirements")

            # Hash password and generate verification code
            hashed_password = get_password_hash(form_data.password)
            verification_code = get_verification_code()
            # Add user to databasehttp://localhost:8000/verify-email?token=0c435db496334cb5439c4e576f00360e3c1a0a955b2a8e4f302e80e39b859130
            cursor.execute(f"SELECT insert_persona('{form_data.email}','{form_data.nombre}','{form_data.telefono}','{hashed_password}',false,'{verification_code}','{form_data.apellido}');")
            conexion.commit()
            
            # Send verification email
            email = EmailMessage()
            email["From"] = configuraciones.mail_sender
            email["To"] = form_data.email
            email["Subject"] = "Verificacion de cuenta"
            email.set_content(f"El link de verificacion de su cuenta: https://{configuraciones.api_url}:{configuraciones.api_port}/verify-email?token={verification_code}")
            send_verification_mail(form_data.email, email)
            return {"Usuario creado con exito, revise su correo para verificar su cuenta"}

    except psycopg2.Error as e:
        print("Ocurrió un error al conectar a PostgreSQL: ", e)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/register/empresa", tags=["auth"])
async def registerEmpresa(form_data: Annotated[Empresa, Depends()]):
    try:
        with conexion.cursor() as cursor:
            # Check if user already exists
            user_exist = cursor.execute(f"SELECT usuarioExiste('{form_data.email}')")
            if user_exist:
                raise HTTPException(status_code=400, detail="User already registered")

            # Check password security
            if not is_password_secure(form_data.password):
                raise HTTPException(status_code=400, detail="Password does not meet the security requirements")

            # Hash password and generate verification code
            hashed_password = get_password_hash(form_data.password)
            verification_code = get_verification_code()
            # Add user to database
            cursor.execute(f"SELECT insert_empresa('{form_data.email}','{form_data.nombre}','{form_data.telefono}','{hashed_password}',false,'{verification_code}');")
            conexion.commit()
            
            # Send verification email
            email = EmailMessage()
            email["From"] = configuraciones.mail_sender
            email["To"] = form_data.email
            email["Subject"] = "Verificacion de cuenta"
            email.set_content(f"El link de verificacion de su cuenta: https://{configuraciones.api_url}/verify-email?token={verification_code}")
            send_verification_mail(form_data.email, email)
            return {"Usuario creado con exito, revise su correo para verificar su cuenta"}

    except psycopg2.Error as e:
        print("Ocurrió un error al conectar a PostgreSQL: ", e)
        raise HTTPException(status_code=500, detail="Internal server error")



@router.get("/verify-email", tags=["auth"])
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