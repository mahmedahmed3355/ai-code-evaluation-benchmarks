FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir numpy pandas
COPY environment /app/environment
COPY tests /app/tests
COPY solution /app/solution
RUN cp /app/environment/ml_eval/*.py /app/ml_eval/ && cp /app/solution/ml_eval/*.py /app/ml_eval/
