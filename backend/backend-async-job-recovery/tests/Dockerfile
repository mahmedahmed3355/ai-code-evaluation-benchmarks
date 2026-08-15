FROM python:3.12-slim

WORKDIR /tests

RUN pip install --no-cache-dir \
    pytest==8.4.1 \
    httpx==0.28.1

COPY . /tests/

RUN mkdir -p /logs/verifier
