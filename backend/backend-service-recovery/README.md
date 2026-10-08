# Backend Service Recovery

## Overview

A production-style recovery task involving a FastAPI application, Gunicorn,
systemd, Nginx, and a Unix-domain socket.

The application itself is healthy. The deployment layer has been intentionally
broken and must be repaired without replacing the architecture.

## Objective

Restore the service so that:

- `backend.service` is managed by systemd and remains enabled;
- Gunicorn serves the existing FastAPI application;
- Gunicorn listens on `/run/backend/backend.sock`;
- Nginx remains the public HTTP entry point;
- Nginx proxies to the backend Unix socket;
- `/health` and `/` work through Nginx;
- restarting the backend does not require restarting Nginx;
- the deployment survives a backend service restart;
- access/error logging remains enabled.

## Intended engineering challenge

The visible failure is only the symptom. The agent must inspect the systemd
unit, runtime-directory lifecycle, Unix-socket path, Nginx upstream configuration,
service state, and restart behavior, then repair the deployment while preserving
the application and architecture.

The task deliberately avoids requiring application-code changes or external
services.

## Verification

The verifier checks service state, socket type/path, Nginx syntax and state,
HTTP behavior through the reverse proxy, required proxy headers, service
enablement, and recovery after restarting the backend.

Author: **Mohamed Ahmed**  
Email: **engmohamedelshrbeny@gmail.com**
