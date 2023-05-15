FROM python:alpine3.17

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

# Use ARG for build-time variables and ENV for run-time variables
ARG DB_NAME
ARG USER_DB
ARG PASSWORD_DB
ARG HOST_DB
ARG SECRET_KEY
ARG ALGORITHM
ARG API_URL
ARG MAIL_SENDER
ARG MAIL_PASSWORD
ARG JWE_KEY
ARG MONGODB_URL
ARG MONGODB_NAME
ARG MONGODB_COLLECTION_CART
ARG MONGODB_COLLECTION_PRODUCT

ENV DB_NAME=$DB_NAME \
    USER_DB=$USER_DB \
    PASSWORD_DB=$PASSWORD_DB \
    HOST_DB=$HOST_DB \
    SECRET_KEY=$SECRET_KEY \
    ALGORITHM=$ALGORITHM \
    API_URL=$API_URL \
    MAIL_SENDER=$MAIL_SENDER \
    MAIL_PASSWORD=$MAIL_PASSWORD \
    JWE_KEY=$JWE_KEY \
    MONGODB_URL=$MONGODB_URL \
    MONGODB_NAME=$MONGODB_NAME \
    MONGODB_COLLECTION_CART=$MONGODB_COLLECTION_CART \
    MONGODB_COLLECTION_PRODUCT=$MONGODB_COLLECTION_PRODUCT

# Write the env variables to a .env file in the app directory

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]