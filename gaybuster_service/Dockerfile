FROM python:3.6.9

WORKDIR /app/

RUN apt-get update
RUN pip install poetry
RUN apt-get install -y cmake

RUN pip install dlib tensorflow

ADD ./pyproject.toml /app/
ADD ./poetry.lock /app/

RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi
ADD ./service /app/service