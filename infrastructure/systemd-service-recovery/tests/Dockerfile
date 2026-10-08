FROM python:3.12-slim
WORKDIR /app
COPY environment /app/environment
COPY tests /app/tests
COPY solution /app/solution
RUN chmod +x /app/environment/validate.sh /app/solution/solve.sh /app/tests/test.sh
CMD ["/app/tests/test.sh"]
