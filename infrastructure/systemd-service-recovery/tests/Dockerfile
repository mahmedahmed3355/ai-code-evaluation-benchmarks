FROM python:3.12-slim
WORKDIR /app
COPY environment /app/environment
COPY tests /app/tests
COPY solution /app/solution
RUN chmod +x /app/environment/validate.sh /app/solution/solve.sh /app/tests/test.sh
RUN useradd --create-home --uid 10001 benchmark
USER benchmark
CMD ["/app/tests/test.sh"]
