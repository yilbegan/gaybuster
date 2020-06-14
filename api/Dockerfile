FROM python:3.7-alpine

RUN apk add git gcc musl-dev make cmake libffi-dev openssl-dev
RUN pip install poetry

ADD ./pyproject.toml /server/
ADD ./poetry.lock /server/

WORKDIR /server/

RUN apk add build-base
RUN poetry config virtualenvs.create false && poetry install

ADD ./app /server/app/
