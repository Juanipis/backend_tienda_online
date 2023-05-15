# Library for working with dates and times
from datetime import datetime, timedelta
# Library for connecting and executing queries with PostgreSQL
import psycopg2
# Local module for configuring the database connection and the environment variables
from app.config import ConexionPostgres, Configuraciones
# Library for defining annotated types
from typing import Annotated
# Local module for defining the data model of the user registration
from app.models import UserRegister
# Library for encrypting and verifying passwords
from passlib.context import CryptContext
# Library for encoding and decoding JWT and JWE tokens
from jose import jwt,jwe
# Library for creating and managing API routes
from fastapi import APIRouter, Depends, HTTPException
# Library for working with regular expressions
import re
# Library for sending emails via SMTP protocol
import smtplib 
# Library for creating email messages
from email.message import EmailMessage


router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def create_register_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Configuraciones.SECRET_KEY, algorithm=Configuraciones.ALGORITHM)
    return encoded_jwt


def encrypt_register_token(token: str):
    encrypted = jwe.encrypt(token, Configuraciones.JWE_KEY, algorithm='dir', encryption='A128GCM')
    return encrypted

def decrypt_register_token(token: str):
    try:
        decrypted = jwe.decrypt(token, Configuraciones.JWE_KEY)
        return decrypted
    except:
        raise HTTPException(status_code=400, detail="Token invalido")


def get_password_hash(password):
    return pwd_context.hash(password)

def is_password_secure(password: str):
    return bool(re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$', password))



def send_verification_mail(reciver:str, email:EmailMessage):
    smtp = smtplib.SMTP_SSL("smtp.gmail.com")
    smtp.login(Configuraciones.MAIL_SENDER, Configuraciones.MAIL_PASSWORD)
    smtp.sendmail(Configuraciones.MAIL_SENDER, reciver, email.as_string())
    smtp.quit()

@router.post("/register", tags=["auth"])
async def registerPersona(form_data: Annotated[UserRegister, Depends()]):
    try:
        with ConexionPostgres.cursor() as cursor:
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
                    raise HTTPException(status_code=400, detail="Apellido is required")
            # Create jwe token with user data and send it to user email
            # 1. Create expiration time for token
            access_token_expires = timedelta(minutes=Configuraciones.REGISTER_EXPIRATION_TIME)
            # 2. Hash password
            form_data.password = get_password_hash(form_data.password)
            print(form_data)
            # 3. Create register token
            register_token = create_register_token(form_data.dict(), expires_delta=access_token_expires)
            #4. Encrypt register token
            encrypt_token = encrypt_register_token(register_token)
            #5. Send verification email
            email = EmailMessage()
            email["From"] = Configuraciones.mail_sender
            email["To"] = form_data.email
            email["Subject"] = "Verificacion de cuenta"
            email.set_content(f"El link de verificacion de su cuenta: https://{Configuraciones.API_URL}:{Configuraciones.API_PORT}/register/verify-email?token={encrypt_token.decode()}")
            send_verification_mail(form_data.email, email)
            return {"Usuario creado con exito, revise su correo para verificar su cuenta"}

    except psycopg2.Error as e:
        print("Ocurrió un error al conectar a PostgreSQL: ", e)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/register/verify-email", tags=["auth"])
async def verify_email(token: str):
    try:
        # 1. Decrypt token
        token_jwt = decrypt_register_token(token)
        # 2. Decode token
        userInfo = jwt.decode(token_jwt, Configuraciones.SECRET_KEY, algorithms=[Configuraciones.ALGORITHM])
        # 3. Create user in database
        with ConexionPostgres.cursor() as cursor:
            cursor.execute(f"SELECT insert_usuario('{userInfo['email']}', '{userInfo['nombre']}', '{userInfo['telefono']}', '{userInfo['password']}', true, '{userInfo['apellido']}', {userInfo['person']});")
            ConexionPostgres.commit()
        return {"Usuario creado con exito"}
    except psycopg2.Error as e:
        print("Ocurrió un error al conectar a PostgreSQL: ", e)
        raise HTTPException(status_code=500, detail="Error al actualizar usuario en la base de datos")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token invalido")