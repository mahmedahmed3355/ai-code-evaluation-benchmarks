FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir pytest
COPY environment /app/environment
COPY solution /app/solution
COPY tests /app/tests
ENV PYTHONPATH=/app
CMD ["/app/tests/test.sh"]
