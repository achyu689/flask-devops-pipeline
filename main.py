"""Simple Flask app used to demonstrate a DevOps pipeline."""
import os
import socket
import time

from flask import Flask, Response, jsonify
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

app = Flask(__name__)

APP_VERSION = os.getenv("APP_VERSION", "dev")

REQUEST_COUNT = Counter(
    "app_requests_total", "Total HTTP requests", ["endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds", "Request latency in seconds", ["endpoint"]
)


@app.route("/")
def index():
    start = time.time()
    body = {
        "message": "Hello from the DevOps demo app!",
        "version": APP_VERSION,
        "pod": socket.gethostname(),
    }
    REQUEST_LATENCY.labels(endpoint="/").observe(time.time() - start)
    REQUEST_COUNT.labels(endpoint="/", status="200").inc()
    return jsonify(body)


@app.route("/health")
def health():
    """Used by Kubernetes liveness and readiness probes."""
    REQUEST_COUNT.labels(endpoint="/health", status="200").inc()
    return jsonify({"status": "ok"})


@app.route("/metrics")
def metrics():
    """Prometheus scrapes this endpoint."""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
