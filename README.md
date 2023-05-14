# Backend para una tienda online 🛒

_Backend necesario para una tienda online_

## Requisitos 🔑
* [Docker 🐋](https://www.docker.com/) 

### Construido con 🛠
* [Python Alpine 3.17 🐍](https://hub.docker.com/_/python)
* [Postgres 🐘](https://hub.docker.com/_/postgres)
* [MongoDB 🍃](https://hub.docker.com/_/mongo)

#### Librerías 📚
* [FastAPI ⚡](https://fastapi.tiangolo.com/)
* [Pydantic 💃](https://docs.pydantic.dev/)
* [Uvicorn 🦄](https://www.uvicorn.org/)

#### Despliegue 🔌
En la carpeta raíz es necesario un archivo de variable de entorno en la raíz del proyecto .env que contenga las siguientes variables de entorno:
```
dbname=
userdb=
passworddb=
hostdb=
portdb=
secret_key=
algorithm=
acces_token_expire_minutes=
api_url=
api_port=
mail_sender=
mail_password=
jwe_key=
register_expiration_time=
mongodb_url=
mongodb_name=
mongodb_collection_cart=
mongodb_collection_product=
```
Para ejecutar el código
```
uvicorn app.main:app 
```

#### Autores ✏
👨‍💻 Juan Pablo Díaz Correa - [@Juanipis](https://github.com/Juanipis) - juanipis@gmail.com
