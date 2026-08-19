FROM python:3.12-slim

WORKDIR /workspace

COPY requirements.lock .
RUN pip install --no-cache-dir -r requirements.lock

COPY . .

CMD ["make", "validate-all"]

# Run as an unprivileged user.
RUN useradd --create-home --uid 10001 benchmark
USER benchmark

