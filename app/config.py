from pydantic import BaseSettings
import psycopg2


class Settings(BaseSettings):
    """
    Settings - Clase para obtener las variables de entorno del sistema
    """
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
    jwe_key: str
    register_expiration_time: int
    mongodb_url: str
    mongodb_name: str
    mongodb_collection_cart: str
    mongodb_collection_product: str
    class Config:
        env_file = ".env"

Configuraciones = Settings()

try:
    credenciales = {
        "dbname": Configuraciones.dbname,
        "user": Configuraciones.userdb,
        "password": Configuraciones.passworddb,
        "host": Configuraciones.hostdb,
        "port": Configuraciones.portdb
    }
    ConexionPostgres = psycopg2.connect(**credenciales)
except psycopg2.Error as e:
    print("Ocurrió un error al conectar a PostgreSQL: ", e)