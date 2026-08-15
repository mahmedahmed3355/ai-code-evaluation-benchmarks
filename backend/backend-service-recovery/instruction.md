# Backend Service Recovery

A production backend service behind an Nginx reverse proxy is currently unhealthy.

The backend application is implemented with FastAPI and served by Gunicorn through a Unix domain socket. Nginx is responsible for exposing the service over HTTP.

Diagnose the deployment and restore the existing architecture without replacing the backend server or removing Nginx.

The recovered deployment must:

- serve the backend through Nginx;
- expose a healthy `/health` endpoint;
- keep the backend managed by systemd;
- use the existing Unix socket architecture;
- remain functional after restarting the backend service.

Do not modify the application code.
Do not replace Nginx with another web server.
Do not bypass the reverse proxy.
