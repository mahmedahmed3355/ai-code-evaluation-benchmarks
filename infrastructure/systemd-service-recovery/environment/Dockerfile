FROM python:3.12-slim
WORKDIR /app
COPY app /app/app
COPY runtime /app/runtime
COPY systemd /app/systemd
COPY validate.sh /app/validate.sh
RUN chmod +x /app/validate.sh
RUN useradd --create-home --uid 10001 benchmark
USER benchmark
CMD ["/app/validate.sh"]
