FROM python:3.10-slim


ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWEITEBYTECODE=1

WORKDIR /app

RUN pip install --upgrade pip --no-cache-dir && \
pip install poetry --no-cache-dir && \
poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root

COPY . .
