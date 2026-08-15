FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    coreutils \
    grep \
    sed \
    diffutils \
    findutils \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p \
    /app/configs \
    /app/scripts \
    /app/logs \
    /app/build \
    /app/artifacts \
    /app/reports

COPY data/configs/ /app/configs/
COPY data/scripts/ /app/scripts/
COPY data/logs/ /app/logs/
COPY data/build/ /app/build/
COPY data/artifacts/ /app/artifacts/
COPY data/reports/ /app/reports/

RUN chmod +x /app/scripts/*.sh /app/scripts/*.py

WORKDIR /app

CMD ["/bin/bash"]
