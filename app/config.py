from pydantic import BaseSettings
import psycopg2


class Settings(BaseSettings):
    """
    Settings - Clase para obtener las variables de entorno del sistema
    """
    DB_NAME: str
    USER_DB: str 
    PASSWORD_DB: str
    HOST_DB: str 
    PORT_DB:int=5432
    SECRET_KEY: str
    ALGORITHM: str 
    ACCESS_TOKEN_EXPIRATION_TIME:int=30 
    API_URL: str
    API_PORT:int=443
    MAIL_SENDER: str
    MAIL_PASSWORD: str
    JWE_KEY: str
    REGISTER_EXPIRATION_TIME:int=3
    MONGODB_URL: str
    MONGODB_NAME: str
    MONGODB_COLLECTION_CART: str
    MONGODB_COLLECTION_PRODUCT: str
    class Config:
        env_file = ".env"

Configuraciones = Settings()

try:
    credenciales = {
        "dbname": Configuraciones.DB_NAME,
        "user": Configuraciones.USER_DB,
        "password": Configuraciones.PASSWORD_DB,
        "host": Configuraciones.HOST_DB,
        "port": Configuraciones.PORT_DB
    }
    ConexionPostgres = psycopg2.connect(**credenciales)
except psycopg2.Error as e:
    print("Ocurrió un error al conectar a PostgreSQL: ", e)