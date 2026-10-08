FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends bash coreutils grep sed diffutils findutils && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /app/configs /app/datasets /app/logs /app/build /app/artifacts /app/reports /app/scripts
COPY data/configs/ /app/configs/
COPY data/datasets/ /app/datasets/
COPY data/history/ /app/history/
COPY data/scripts/ /app/scripts/
RUN chmod +x /app/scripts/*.sh /app/scripts/*.py
RUN useradd --create-home --uid 10001 benchmark
USER benchmark
