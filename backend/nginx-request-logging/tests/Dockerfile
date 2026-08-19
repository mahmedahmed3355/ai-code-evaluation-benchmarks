FROM python:3.13-slim-bookworm

WORKDIR /tests

RUN pip install --no-cache-dir \
    pytest==8.4.1 \
    requests==2.32.4 \
    pytest-json-ctrf==0.3.5

COPY . /tests/

RUN mkdir -p /logs/verifier

# Run as an unprivileged user.
RUN useradd --create-home --uid 10001 benchmark
USER benchmark

