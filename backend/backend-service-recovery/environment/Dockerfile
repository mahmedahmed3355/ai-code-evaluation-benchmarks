FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    nginx \
    systemd \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/backend-venv && \
    /opt/backend-venv/bin/pip install --no-cache-dir \
    fastapi==0.116.1 \
    gunicorn==23.0.0 \
    uvicorn==0.35.0

RUN mkdir -p \
    /app \
    /var/log/backend

COPY app.py /app/app.py
COPY backend.service /etc/systemd/system/backend.service
COPY nginx.conf /etc/nginx/sites-available/backend

RUN ln -sf /etc/nginx/sites-available/backend \
    /etc/nginx/sites-enabled/backend && \
    rm -f /etc/nginx/sites-enabled/default && \
    ln -sf /lib/systemd/system/nginx.service \
    /etc/systemd/system/multi-user.target.wants/nginx.service

WORKDIR /app

CMD ["/lib/systemd/systemd"]

# Run as an unprivileged user.
RUN useradd --create-home --uid 10001 benchmark
USER benchmark

