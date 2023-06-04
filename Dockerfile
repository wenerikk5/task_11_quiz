FROM python:3.11.1-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

COPY ./app app
COPY ./alembic alembic
COPY alembic.ini .env ./
