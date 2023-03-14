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
Para backendVars.env
dbname=yours_db_name
userdb=yours_user_db
passworddb=yours_password_db
hostdb=yours_host_db
portdb=yours_port_db
```
```
Para postgresVars.env
POSTGRES_USER=yours_user_db
POSTGRES_PASSWORD=yours_password_db
POSTGRES_DB=yours_db_name
```
```
Para pgadminVars.env (cuando se despliegue es importante eliminar)
PGADMIN_DEFAULT_EMAIL=yours_email
PGADMIN_DEFAULT_PASSWORD=yours_password
```

Se recomienda cambiar los valores. Esta una app basada en contenedores, para desplegarla en local una opción es:\
Primero se crea la imagen del backed que se usará en el docker-compose
```
docker build -t <nombre>/<etiqueta> .
```
Luego se despliega el docker-compose (el -d es para que se ejecute en segundo plano)
```
docker compose up -d
```
Si se hacen cambios en el código se debe reconstruir la imagen y luego reiniciar el contenedor
```
docker compose up -d --build
```
En caso de que nada funcione se puede eliminar el contenedor y volver a crearlo
```
docker-compose down
docker compose up  --force-recreate
```

#### Autores ✏
👨‍💻 Juan Pablo Díaz Correa - [@Juanipis](https://github.com/Juanipis) - juanipis@gmail.com
