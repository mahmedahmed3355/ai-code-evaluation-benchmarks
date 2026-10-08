# Backend Service Recovery

A production backend service behind an Nginx reverse proxy is currently
unhealthy.

The backend application is a FastAPI service served by Gunicorn through a Unix
domain socket. Nginx is the only public HTTP entry point, and systemd owns the
backend service lifecycle.

The deployment has multiple configuration defects. Diagnose the system rather
than replacing components, and restore the existing architecture.

## Required final state

The recovered deployment must:

1. Serve the existing FastAPI application through Nginx.
2. Keep `backend.service` managed and enabled by systemd.
3. Run Gunicorn with the existing Uvicorn worker architecture.
4. Use `/run/backend/backend.sock` as the backend Unix socket.
5. Keep the Unix socket usable by Nginx.
6. Keep Nginx as the HTTP reverse proxy.
7. Make both `/health` and `/` reachable through Nginx.
8. Preserve the existing API responses.
9. Forward the normal reverse-proxy request headers already present in the
   configuration.
10. Continue serving traffic after `systemctl restart backend.service`.
11. Keep backend access/error logs enabled.
12. Do not require restarting Nginx after a backend restart.

## Constraints

- Do not modify `/app/app.py`.
- Do not replace FastAPI, Gunicorn, Nginx, or systemd.
- Do not bypass Nginx by exposing Gunicorn on a TCP port.
- Do not remove the Unix socket architecture.
- Do not hard-code a test response in Nginx.
- Do not replace the proxy with a second HTTP server.
- Do not disable systemd service management.
- Do not modify `/tests`.
- Do not depend on external services.
- Do not depend on state outside the container.
- Preserve the existing application behavior.

## Success criteria

A correct solution must work from a clean task environment and remain correct
after the backend service is restarted. The final state should be a normal,
maintainable production deployment rather than a one-shot workaround.

The important engineering problems are service lifecycle, runtime-directory
creation, Unix-socket addressing and permissions, Nginx upstream correctness,
and restart-safe service management.
