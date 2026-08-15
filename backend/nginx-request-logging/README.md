# Nginx Request Logging

## Overview

This task requires configuring an Nginx web server for an internal documentation portal with advanced request logging, custom error handling, and traffic management. The agent must install Nginx, configure it to listen on port **9090**, serve static files from **`/srv/docs`**, implement detailed request logging, configure rate limiting, create a custom 404 page, and verify the server is running correctly.

## Skills Tested

- **Web Server Administration**: Installing and configuring Nginx
- **Configuration Management**: Creating and editing Nginx configuration files
- **Custom Logging**: Configuring custom log formats and log destinations
- **Rate Limiting**: Configuring request rate limiting using `limit_req_zone` and `limit_req`
- **File System Operations**: Creating directories and static HTML content
- **Service Management**: Testing, starting, and restarting Nginx
- **Troubleshooting**: Validating configuration syntax before deployment

## Environment Details

- **Base Image**: `python:3.13-slim-bookworm`
- **Pre-installed Tools**: Python 3.13, curl, requests
- **Resources**: 1 CPU, 2 GB RAM, 10 GB Storage
- **Network**: Internet access enabled
- **Timeout**: 15 minutes for both agent and verifier

## Verification

The verifier (`test_outputs.py`) validates that:

1. Nginx is installed.
2. Nginx is running and accessible on **localhost:9090**.
3. The index page returns exactly:

   ```
   Welcome to the Internal Documentation Portal
   ```

4. A nonexistent page returns HTTP 404 and the custom page:

   ```
   Resource not found
   ```

5. The Nginx configuration is syntactically valid.
6. The server configuration:
   - Listens on **port 9090**
   - Uses **`/srv/docs`** as the document root
   - Stores configuration in **`/etc/nginx/conf.d/docs-site.conf`**
7. The global Nginx configuration contains:
   - A custom `log_format` including:
     - `$time_local`
     - `$request_method`
     - `$status`
     - `$http_user_agent`
   - A `limit_req_zone` configured with:
     - **20 requests/second**
     - **10 MB memory zone**
8. Access logs are written to:

   ```
   /var/log/nginx/docs-access.log
   ```

9. Access log entries contain:
   - Timestamp
   - HTTP method
   - Status code
   - User-Agent

## Expected Configuration Summary

| Setting | Expected Value |
|---------|----------------|
| Listen Port | 9090 |
| Document Root | `/srv/docs` |
| Config File | `/etc/nginx/conf.d/docs-site.conf` |
| Access Log | `/var/log/nginx/docs-access.log` |
| Error Log | `/var/log/nginx/docs-error.log` |
| Rate Limit | 20 requests/sec |
| Burst | 5 |
| Zone Size | 10 MB |
| Index Page | Welcome to the Internal Documentation Portal |
| 404 Page | Resource not found |

The verifier uses **pytest** together with **pytest-json-ctrf** to execute the validation suite and produce CTRF-compatible results.
