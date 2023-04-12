from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Annotated
from app.routers.auth import get_current_active_user
from app.config import conexion, configuraciones
import psycopg2

class UserInfo(BaseModel):
  email: str
  nombre: str = None
  telefono: str = None
class User(BaseModel):
    email: str | None = None
    id: int | None = None
    enabled: bool | None = None

router = APIRouter()

async def get_user_info_db(user_id:int):
  try:
    with conexion.cursor() as cursor:
      cursor.execute(f'select email,nombre,telefono from usuarios where id=\'{user_id}\';')
      email_db = cursor.fetchone()
      if(email_db != None):
        return UserInfo(email=email_db[0],nombre=email_db[1],telefono=email_db[2])
      else:
        return None
  except psycopg2.Error as e:
    print("Ocurrió un error al conectar a PostgreSQL: ", e)

@router.post("/info_user", response_model=UserInfo,tags=["info_user"])
async def get_info_user(current_user: Annotated[User, Depends(get_current_active_user)]):
  if not current_user:
    raise HTTPException(status_code=401, detail="Unauthorized")
  else:
    return await get_user_info_db(current_user.id)
