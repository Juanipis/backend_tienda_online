# Backend para una tienda online 🛒

_Backend necesario para una tienda online_

## Requisitos 🔑
* [Docker 🐋](https://www.docker.com/) 

### Construido con 🛠
* [Python Alpine 3.17 🐍](https://hub.docker.com/_/python)
* [Postgres 🐘](https://hub.docker.com/_/postgres)
* [Mongo 🐒](https://hub.docker.com/_/mongo)

#### Librerías 📚
* [FastAPI ⚡](https://fastapi.tiangolo.com/)
* [Pydantic 💃](https://docs.pydantic.dev/)
* [Uvicorn 🦄](https://www.uvicorn.org/)

#### Despliegue 🔌
En la carpeta raíz es necesario un archivo .env que contenga las siguientes variables de entorno:
```
POSTGRES_USER='postgres'
POSTGRES_PASSWORD='example'
PGADMIN_DEFAULT_EMAIL='example@example.com'
PGADMIN_DEFAULT_PASSWORD='example'
```
Se recomienda cambiar los valores. Esta una app basada en contenedores, para desplegarla en local una opción es:
```
docker compose up
```
#### Autores ✏
👨‍💻 Juan Pablo Díaz Correa - [@Juanipis](https://github.com/Juanipis) - juanipis@gmail.com
