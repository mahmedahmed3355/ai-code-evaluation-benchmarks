FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    fastapi==0.116.1 \
    uvicorn==0.35.0 \
    pydantic==2.11.7 \
    httpx==0.28.1

COPY app/ /app/

RUN mkdir -p /data

ENV PYTHONUNBUFFERED=1
ENV JOB_DB_PATH=/data/jobs.db
