FROM python:3.12-slim
WORKDIR /app
COPY . /app
ENV APP_VERSION=2.4.1
RUN chmod -R 777 /app
USER root
CMD ["python","app.py"]
