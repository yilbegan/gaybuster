FROM python:3.7-alpine

RUN apk add git gcc musl-dev make cmake libffi-dev openssl-dev
RUN pip install poetry

ADD ./pyproject.toml /telegram/
ADD ./poetry.lock /telegram/

WORKDIR /telegram/

RUN apk add build-base
RUN poetry config virtualenvs.create false && poetry install

ADD ./jetbrains-mono.ttf /telegram/
ADD ./app /telegram/app/
