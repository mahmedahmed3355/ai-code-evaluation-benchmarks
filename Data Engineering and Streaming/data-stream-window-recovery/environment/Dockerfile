FROM python:3.12-slim
WORKDIR /app
COPY data /app/data
COPY streaming /app/streaming
ENV PYTHONPATH=/app
CMD ["python","-m","streaming.cli","--events","/app/data/events.jsonl","--state","/app/data/state.json","--checkpoint","/app/data/checkpoint.json","--output","/app/data/output.json","--dlq","/app/data/dlq.jsonl","--config","/app/data/config.json"]
