# Production Orders API Recovery

A system-level backend reliability task for coding-agent evaluation.

The candidate receives a healthy FastAPI application embedded in a deliberately broken production deployment. The intended stack is:

`systemd → Gunicorn/Uvicorn → Unix domain socket → Nginx → HTTP client`

The task requires recovering the deployment without changing application behavior or replacing infrastructure components.

## What makes it difficult

The failure is distributed across service lifecycle, environment loading, Unix-socket permissions, socket naming, and Nginx routing. A locally plausible fix can still fail after restart, under a clean boot, or when the API path is forwarded through the proxy.

## Evaluation

The verifier checks service state, process identity, environment propagation, socket type and permissions, Nginx configuration, proxy routing, API semantics, 404 preservation, backend restart recovery, repeated restart recovery, and direct-backend isolation.

## Environment

CPU-only Ubuntu 24.04 container. No external services or network access are required.

## Author

Mohamed Ahmed — engmohamedelshrbeny@gmail.com
