FROM python:3.13-slim-bookworm

RUN pip install --no-cache-dir pytest

COPY . /tests/

RUN mkdir -p \
    /app/src \
    /logs/verifier

WORKDIR /app

# Run as an unprivileged user.
RUN useradd --create-home --uid 10001 benchmark
USER benchmark

