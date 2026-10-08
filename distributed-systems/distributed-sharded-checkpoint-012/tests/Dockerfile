FROM python:3.11-slim
WORKDIR /app
COPY environment/app/ /app/app/
COPY tests/ /app/tests/
ENV PYTHONPATH=/app
RUN python -m compileall -q /app/app /app/tests
CMD ["python", "/app/tests/test_runner.py"]
