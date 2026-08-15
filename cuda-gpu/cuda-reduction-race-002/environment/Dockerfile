FROM python:3.13-slim-bookworm

WORKDIR /app

COPY data/reduction.cu /app/src/reduction.cu
COPY data/reduction_test.cu /app/src/reduction_test.cu
COPY data/run_reduction.sh /app/run_reduction.sh

RUN chmod +x /app/run_reduction.sh \
    && pip install --no-cache-dir pytest
