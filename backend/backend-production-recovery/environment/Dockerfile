FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-venv nginx systemd curl ca-certificates procps iproute2 \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv /opt/backend-venv && /opt/backend-venv/bin/pip install --no-cache-dir \
    fastapi==0.116.1 gunicorn==23.0.0 uvicorn==0.35.0
RUN useradd --system --home /nonexistent --shell /usr/sbin/nologin backend && \
    mkdir -p /app /etc/backend /var/log/backend /run/backend && \
    chown -R backend:backend /app /etc/backend /var/log/backend /run/backend
COPY app.py /app/app.py
COPY backend.service /etc/systemd/system/backend.service
COPY backend.env /etc/backend/backend.env
COPY nginx.conf /etc/nginx/sites-available/backend
RUN ln -sf /etc/nginx/sites-available/backend /etc/nginx/sites-enabled/backend && \
    rm -f /etc/nginx/sites-enabled/default && \
    systemctl enable nginx.service
WORKDIR /app
CMD ["/lib/systemd/systemd"]
