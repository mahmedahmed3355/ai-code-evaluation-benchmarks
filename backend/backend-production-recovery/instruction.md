# Production Orders API Recovery

A production-style Orders API is failing after a deployment change. The application itself is known-good and must not be modified. The service is intended to run as a multi-worker Gunicorn/Uvicorn process managed by systemd and exposed only through Nginx over a Unix domain socket.

Restore the deployment so that the existing application works reliably under the intended architecture.

## Required behavior

- `GET /health` returns HTTP 200 with JSON containing `status: ok`.
- `GET /ready` returns HTTP 200 with JSON containing `ready: true`.
- `GET /api/v1/orders/A-100` returns HTTP 200 and the existing order data.
- `GET /api/v1/orders/B-200` returns HTTP 200 and the existing order data.
- An unknown order continues to return HTTP 404.
- `GET /api/v1/runtime` must expose the configured `BACKEND_BOOT_ID` value.
- The public HTTP interface is Nginx; clients must not need direct access to Gunicorn.

## Deployment invariants

- Keep FastAPI, Gunicorn, Uvicorn workers, Nginx, systemd, and the Unix-domain-socket architecture.
- The backend must be managed by `backend.service`.
- Gunicorn must run as the existing `backend` service account.
- The socket must be created under `/run/backend/` and be usable by Nginx without making the socket world-writable.
- The service must load `/etc/backend/backend.env`.
- Nginx must proxy `/health`, `/ready`, and `/api/` to the backend through the Unix socket.
- `/api/...` paths must arrive at FastAPI unchanged.
- Restarting `backend.service` must not require restarting Nginx.
- Repeated backend restarts must recover automatically.
- Nginx must remain the only public HTTP entry point.
- Do not replace the Unix socket with TCP or another IPC mechanism.
- Do not modify `/app/app.py`.
- Do not add a second web server or bypass Nginx.
- Do not hard-code responses in Nginx.
- Do not weaken permissions just to make the socket work.
- Do not modify `/tests`.
- Do not depend on external services or internet access.

The incident is intentionally represented by interacting deployment defects rather than a single incorrect line. Diagnose the service manager, runtime environment, socket lifecycle/permissions, and reverse-proxy routing as one system. The correct repair should remain valid after a clean container boot and after backend restarts.
