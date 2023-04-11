# Backend para una tienda online 🛒

_Backend necesario para una tienda online_

## Requisitos 🔑
* [Docker 🐋](https://www.docker.com/) 

### Construido con 🛠
* [Python Alpine 3.17 🐍](https://hub.docker.com/_/python)
* [Postgres 🐘](https://hub.docker.com/_/postgres)

#### Librerías 📚
* [FastAPI ⚡](https://fastapi.tiangolo.com/)
* [Pydantic 💃](https://docs.pydantic.dev/)
* [Uvicorn 🦄](https://www.uvicorn.org/)

#### Despliegue 🔌
En la carpeta raíz es necesario un archivo tres archivos distintos .env que contenga las siguientes variables de entorno:
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
```
```
uvicorn app.main:app --reload --ssl-keyfile "ruta.pem" --ssl-certfile "ruta.pem"
```
#### Autores ✏
👨‍💻 Juan Pablo Díaz Correa - [@Juanipis](https://github.com/Juanipis) - juanipis@gmail.com
