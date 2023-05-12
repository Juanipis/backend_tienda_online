from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
import re
import psycopg2
import smtplib 
from email.message import EmailMessage
from app.config import ConexionPostgres, Configuraciones
from typing import Annotated
from jose import jwt,jwe
from app.models import UserRegister

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def create_register_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, Configuraciones.secret_key, algorithm=Configuraciones.algorithm)
    return encoded_jwt


def encrypt_register_token(token: str):
    encrypted = jwe.encrypt(token, Configuraciones.jwe_key, algorithm='dir', encryption='A128GCM')
    return encrypted

def decrypt_register_token(token: str):
    try:
        decrypted = jwe.decrypt(token, Configuraciones.jwe_key)
        return decrypted
    except:
        raise HTTPException(status_code=400, detail="Token invalido")


def get_password_hash(password):
    return pwd_context.hash(password)

def is_password_secure(password: str):
    return bool(re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$', password))



def send_verification_mail(reciver:str, email:EmailMessage):
    smtp = smtplib.SMTP_SSL("smtp.gmail.com")
    smtp.login(Configuraciones.mail_sender, Configuraciones.mail_password)
    smtp.sendmail(Configuraciones.mail_sender, reciver, email.as_string())
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
            access_token_expires = timedelta(minutes=Configuraciones.register_expiration_time)
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
            email.set_content(f"El link de verificacion de su cuenta: https://{Configuraciones.api_url}:{Configuraciones.api_port}/register/verify-email?token={encrypt_token.decode()}")
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
        userInfo = jwt.decode(token_jwt, Configuraciones.secret_key, algorithms=[Configuraciones.algorithm])
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