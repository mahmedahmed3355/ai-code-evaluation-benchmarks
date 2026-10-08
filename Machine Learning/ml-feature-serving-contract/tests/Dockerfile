FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir numpy
COPY environment /app/environment
COPY tests /app/tests
COPY solution /solution
RUN cp /app/environment/ml_service/*.py /app/ml_service/
RUN chmod +x /app/tests/test.sh /solution/solve.sh
CMD ["/app/tests/test.sh"]
