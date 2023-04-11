from pydantic import BaseSettings
import psycopg2

class Settings(BaseSettings):
    dbname: str
    userdb: str 
    passworddb: str
    hostdb: str 
    portdb: int 
    secret_key: str
    algorithm: str 
    acces_token_expire_minutes: int 
    api_url: str
    api_port: int
    mail_sender: str
    mail_password: str
    class Config:
        env_file = ".env"

configuraciones = Settings()

try:
    credenciales = {
        "dbname": configuraciones.dbname,
        "user": configuraciones.userdb,
        "password": configuraciones.passworddb,
        "host": configuraciones.hostdb,
        "port": configuraciones.portdb
    }
    conexion = psycopg2.connect(**credenciales)
except psycopg2.Error as e:
    print("Ocurrió un error al conectar a PostgreSQL: ", e)