FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    systemd \
    nginx \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages \
    pytest==8.4.1 \
    pytest-json-ctrf==0.3.5

WORKDIR /tests

COPY test_outputs.py /tests/test_outputs.py
COPY test.sh /tests/test.sh

RUN chmod +x /tests/test.sh

ENTRYPOINT ["/tests/test.sh"]

# Run as an unprivileged user.
RUN useradd --create-home --uid 10001 benchmark
USER benchmark

