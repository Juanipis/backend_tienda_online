FROM python:alpine3.17

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

# Use ARG for build-time variables and ENV for run-time variables
ARG dbname
ARG userdb
ARG passworddb
ARG hostdb
ARG portdb
ARG secret_key
ARG algorithm
ARG acces_token_expire_minutes
ARG api_url
ARG api_port
ARG mail_sender
ARG mail_password
ARG jwe_key
ARG register_expiration_time
ARG mongodb_url
ARG mongodb_name
ARG mongodb_collection_cart
ARG mongodb_collection_product

ENV dbname=$dbname \
    userdb=$userdb \
    passworddb=$passworddb \
    hostdb=$hostdb \
    portdb=$portdb \
    secret_key=$secret_key \
    algorithm=$algorithm \
    acces_token_expire_minutes=$acces_token_expire_minutes \
    api_url=$api_url \
    api_port=$api_port \
    mail_sender=$mail_sender \
    mail_password=$mail_password \
    jwe_key=$jwe_key \
    register_expiration_time=$register_expiration_time \
    mongodb_url=$mongodb_url \
    mongodb_name=$mongodb_name \
    mongodb_collection_cart=$mongodb_collection_cart \
    mongodb_collection_product=$mongodb_collection_product

# Write the env variables to a .env file in the app directory


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
