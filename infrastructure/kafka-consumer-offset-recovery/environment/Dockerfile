FROM python:3.12-slim-bookworm
WORKDIR /app
COPY data/ /app/data/
RUN for f in /app/data/*.json; do python3 -m json.tool "$f" >/dev/null; done \
 && useradd --create-home --uid 10001 appuser \
 && chown -R appuser:appuser /app
USER appuser
