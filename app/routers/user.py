from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Annotated
from app.routers.auth import get_current_active_user
from app.config import conexion
import psycopg2

class UserInfo(BaseModel):
  email: str
  nombre: str
  telefono: str
  is_persona: bool
  enabled: bool
  apellido: str = None
  
class User(BaseModel):
    email: str | None = None
    id: int | None = None
    enabled: bool | None = None

router = APIRouter()

async def get_user_info_db(user_id:int):
  try:
    with conexion.cursor() as cursor:
      cursor.execute(f'select buscar_usuario({user_id});')
      datosUsuario = list(cursor.fetchone()[0].strip('()').split(','))
      
      if datosUsuario[3] == "t":
        datosUsuario[3] = True
      else:
        datosUsuario[3] = False
      
      if datosUsuario[4] == "":  #Si es una empresa
        return UserInfo(email=datosUsuario[0],nombre=datosUsuario[1],telefono=datosUsuario[2],enabled=datosUsuario[3], is_persona=False ,apellido=None)
      else: # Si es una persona
        return UserInfo(email=datosUsuario[0],nombre=datosUsuario[1],telefono=datosUsuario[2],enabled=datosUsuario[3] ,is_persona=True ,apellido=datosUsuario[4])
  except psycopg2.Error as e:
    print("Ocurrió un error al conectar a PostgreSQL: ", e)

@router.post("/info_user",response_model=UserInfo, tags=["info_user"])
async def get_info_user(current_user: Annotated[User, Depends(get_current_active_user)]):
  if not current_user:
    raise HTTPException(status_code=401, detail="Unauthorized")
  else:
    return await get_user_info_db(current_user.id)
