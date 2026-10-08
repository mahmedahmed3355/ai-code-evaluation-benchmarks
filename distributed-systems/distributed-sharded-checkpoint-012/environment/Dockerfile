FROM python:3.11-slim
WORKDIR /app
COPY app/ /app/app/
COPY data/ /app/data/
COPY validate.sh /app/validate.sh
RUN chmod +x /app/validate.sh
ENV PYTHONPATH=/app
CMD ["/app/validate.sh"]
