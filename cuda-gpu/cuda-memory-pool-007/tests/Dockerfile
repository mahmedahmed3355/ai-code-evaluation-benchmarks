FROM python:3.13-slim-bookworm

RUN pip install --no-cache-dir pytest

COPY . /tests/

RUN mkdir -p \
    /app/build \
    /app/artifacts \
    /app/reports \
    /app/configs \
    /app/datasets \
    /logs/verifier

WORKDIR /app
