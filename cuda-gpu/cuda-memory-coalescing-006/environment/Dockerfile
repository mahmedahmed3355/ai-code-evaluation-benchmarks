FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        bash \
        coreutils \
        grep \
        sed \
        diffutils \
        findutils \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p \
    /app/configs \
    /app/datasets \
    /app/logs \
    /app/build \
    /app/artifacts \
    /app/reports \
    /app/scripts

COPY data /root/data
COPY data/configs/ /app/configs/
COPY data/datasets/ /app/datasets/
COPY data/logs/ /app/logs/
COPY data/scripts/ /app/scripts/

RUN chmod +x /app/scripts/*.sh /app/scripts/*.py

WORKDIR /app

# Run as an unprivileged user.
RUN useradd --create-home --uid 10001 benchmark
USER benchmark

