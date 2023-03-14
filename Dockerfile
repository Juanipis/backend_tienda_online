FROM python:alpine3.17

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

ARG dbname
ENV env_name $dbname

ARG userdb
ENV env_name $userdb

ARG passworddb
ENV env_name $dbname

ARG hostdb
ENV env_name $userdb

ARG portdb
ENV env_name $dbname

ARG secret_key
ENV env_name $userdb

ARG algorithm
ENV env_name $dbname

ARG acces_token_expire_minutes
ENV env_name $userdb

RUN echo "DB_NAME=${dbname}" >> /code/app/routers/env.env \
    && echo "DB_USER=${userdb}" >> /code/app/routers/env.env \
    && echo "DB_PASSWORD=${passworddb}" >> /code/app/routers/env.env \
    && echo "DB_HOST=${hostdb}" >> /code/app/routers/env.env \
    && echo "DB_PORT=${portdb}" >> /code/app/routers/env.env \
    && echo "SECRET_KEY=${secret_key}" >> /code/app/routers/env.env \
    && echo "ALGORITHM=${algorithm}" >> /code/app/routers/env.env \
    && echo "ACCESS_TOKEN_EXPIRE_MINUTES=${acces_token_expire_minutes}" >> /code/app/routers/.env


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]