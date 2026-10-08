import os
import time
from fastapi import FastAPI, HTTPException

app = FastAPI()
BOOT_ID = os.environ.get("BACKEND_BOOT_ID", "stable")
STARTED = time.time()
ORDERS = {
    "A-100": {"status": "paid", "total": 1250},
    "B-200": {"status": "processing", "total": 980},
}

@app.get("/health")
def health():
    return {"status": "ok", "service": "orders-api"}

@app.get("/ready")
def ready():
    return {"ready": True, "worker_pid": os.getpid()}

@app.get("/api/v1/orders/{order_id}")
def order(order_id: str):
    item = ORDERS.get(order_id)
    if item is None:
        raise HTTPException(status_code=404, detail="order not found")
    return {"order_id": order_id, **item}

@app.get("/api/v1/runtime")
def runtime():
    return {"boot_id": BOOT_ID, "pid": os.getpid(), "uptime": max(0, time.time() - STARTED)}
