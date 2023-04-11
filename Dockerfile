FROM python:alpine3.17

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app



ARG userdb
ENV env_name $dbname
ARG passworddb
ENV env_name $passworddb
ARG hostdb
ENV env_name $hostdb
ARG portdb
ENV env_name $portdb
ARG secret_key
ENV env_name $secret_key
ARG algorithm
ENV env_name $algorithm
ARG acces_token_expire_minutes
ENV env_name $acces_token_expire_minutes
ARG api_url
ENV env_name $api_url
ARG api_port
ENV env_name $api_port
ARG mail_sender
ENV env_name $mail_sender
ARG mail_password
ENV env_name $mail_password


RUN echo "DB_NAME=${dbname}" >> /code/app/.env \
    && echo "DB_USER=${userdb}" >> /code/app/.env \
    && echo "DB_PASSWORD=${passworddb}" >> /code/app/.env \
    && echo "DB_HOST=${hostdb}" >> /code/app/.env \
    && echo "DB_PORT=${portdb}" >> /code/app/.env \
    && echo "SECRET_KEY=${secret_key}" >> /code/app/.env \
    && echo "ALGORITHM=${algorithm}" >> /code/app/.env \
    && echo "ACCESS_TOKEN_EXPIRE_MINUTES=${acces_token_expire_minutes}" >> /code/app/.env \
    && echo "API_URL=${api_url}" >> /code/app/.env \
    && echo "API_PORT=${api_port}" >> /code/app/.env \
    && echo "MAIL_SENDER=${mail_sender}" >> /code/app/.env \
    && echo "MAIL_PASSWORD=${mail_password}" >> /code/app/.env \ >> /code/app/.env

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
#CMD ["uvicorn", "app.main:app", "--host", "${a pi_url}", "--port", "443"]

