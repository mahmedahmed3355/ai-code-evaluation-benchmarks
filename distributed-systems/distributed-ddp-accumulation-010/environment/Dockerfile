FROM python:3.12-slim
RUN pip install --no-cache-dir torch==2.10.0+cpu --index-url https://download.pytorch.org/whl/cpu
WORKDIR /app
COPY app /app/app
COPY data /app/data
COPY validate.sh /app/validate.sh
RUN chmod +x /app/validate.sh
ENV PYTHONPATH=/app
CMD ["/app/validate.sh"]
