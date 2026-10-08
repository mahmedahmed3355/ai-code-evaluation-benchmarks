FROM python:3.11-slim
WORKDIR /app
COPY data /app/data
COPY ml_promo /app/ml_promo
RUN pip install --no-cache-dir numpy==2.2.3
ENV PYTHONPATH=/app
