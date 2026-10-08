FROM python:3.12.7-slim-bookworm
WORKDIR /app
RUN addgroup --gid 10001 --system app && adduser --uid 10001 --gid 10001 --system --no-create-home app
COPY --chown=10001:10001 app.py /app/app.py
RUN mkdir -p /tmp/service-cache && chown 10001:10001 /tmp/service-cache
ENV APP_VERSION=2.4.1
USER 10001:10001
HEALTHCHECK --interval=30s --timeout=3s --start-period=2s --retries=3 CMD ["python","-c","import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2)"]
CMD ["python","app.py"]
