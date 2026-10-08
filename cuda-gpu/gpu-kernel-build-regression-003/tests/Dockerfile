FROM python:3.12-slim

WORKDIR /tests

RUN pip install --no-cache-dir     pytest==8.4.1     pytest-json-ctrf==0.3.5

COPY test_outputs.py /tests/test_outputs.py
COPY test.sh /tests/test.sh

RUN mkdir -p /logs/verifier     && useradd --create-home --uid 10001 benchmark     && chown -R benchmark:benchmark /logs /tests     && chmod +x /tests/test.sh

USER benchmark

CMD ["/tests/test.sh"]
