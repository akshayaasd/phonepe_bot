from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import (
    multiprocess, CollectorRegistry, Gauge,
    start_http_server
)
from gnani_sdk.config_parser import PROMETHEUS_METRICS_PORT, ENV, PROMETHEUS_MULTIPROC_DIR
from gnani_sdk.logging import setup_logger
from pathlib import Path

logger = setup_logger("metrics")

# Custom gauge for tracking concurrent requests
in_progress_gauge = Gauge(
    "in_progress_requests",
    "In-progress requests by path and method",
    labelnames=["path", "method"],
    multiprocess_mode="livesum"
)

if ENV != "dev":
    Path(PROMETHEUS_MULTIPROC_DIR).mkdir(parents=True, exist_ok=True)
    instrumentator = Instrumentator(
        should_instrument_requests_inprogress=True,
        inprogress_labels=True,
        excluded_handlers=["/health/livecheck", "/health/readycheck"]
    )

def start_metrics_server():
    """Start the /metrics server ONCE in the master process."""
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    start_http_server(port=PROMETHEUS_METRICS_PORT, registry=registry)  # Only in master
    logger.info(f"✅ Prometheus metrics server started on port: {PROMETHEUS_METRICS_PORT}")

def instrument_app_metrics(app):
    """Attach FastAPI middleware in each worker."""
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    instrumentator.registry = registry
    instrumentator.instrument(app).expose(app)
