FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir pytest==8.4.1 pyyaml==6.0.2
COPY test_outputs.py hidden_tests.py /tests/
COPY fixtures/ /app/data/
COPY validate.py /app/validate.py
RUN mkdir -p /logs/verifier
WORKDIR /app
