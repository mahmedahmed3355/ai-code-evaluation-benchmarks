FROM python:3.12-slim
RUN pip install --no-cache-dir torch==2.10.0+cpu pytest==8.4.2 --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir pytest==8.4.2
WORKDIR /app
COPY environment/app /app/app
COPY environment/data /app/data
COPY tests /app/tests
COPY solution /app/solution
ENV PYTHONPATH=/app
CMD ["pytest","-q","/app/tests"]
