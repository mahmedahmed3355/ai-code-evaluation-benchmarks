FROM python:3.11-slim
WORKDIR /app
COPY environment/data /app/data
COPY environment/ml_promo /app/broken_ml_promo
COPY solution/ml_promo /app/ml_promo
COPY tests /app/tests
RUN pip install --no-cache-dir numpy==2.2.3
ENV PYTHONPATH=/app
CMD ["/app/tests/test.sh"]
