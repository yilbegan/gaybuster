FROM python:3.7-alpine

RUN apk add git gcc musl-dev make cmake libffi-dev openssl-dev
RUN pip install poetry

ADD ./pyproject.toml /telegram/
ADD ./poetry.lock /telegram/

WORKDIR /telegram/

RUN apk add build-base
RUN apk add jpeg-dev zlib-dev freetype-dev \
                       lcms2-dev \
                       openjpeg-dev \
                       tiff-dev \
                       tk-dev \
                       tcl-dev \
                       harfbuzz-dev \
                       fribidi-dev
RUN poetry config virtualenvs.create false && poetry install

ADD ./jetbrains-mono.ttf /telegram/
ADD ./app /telegram/app/
