from fastapi import FastAPI
from os import listdir
from shutil import rmtree
from gunicorn.app.base import BaseApplication
import importlib
from gnani_sdk.metrics import start_metrics_server, instrument_app_metrics
from gnani_sdk.tracing import setup_sentry
from gnani_sdk.logging import setup_logger
from gnani_sdk.tracing import instrument_app_tracing
from gnani_sdk.middleware import add_trace_id
from prometheus_client import multiprocess
from gnani_sdk.config_parser import (SENTRY_DSN, SERVER_PORT, SERVER_WORKERS,
                                     GUNICORN_REQUEST_KEEPALIVE, GUNICORN_REQUEST_TIMEOUT, PROMETHEUS_MULTIPROC_DIR, PROJECT_NAME, ENV)

app = FastAPI()

logger = setup_logger("main")

bind = f"0.0.0.0:{SERVER_PORT}"
workers = SERVER_WORKERS
keepalive = GUNICORN_REQUEST_KEEPALIVE
timeout = GUNICORN_REQUEST_TIMEOUT
sentry_dsn = SENTRY_DSN


def when_ready(server):
    if ENV != "dev":
        start_metrics_server()
    logger.info("***** Gunicorn is ready *****")


def child_exit(server, worker):
    multiprocess.mark_process_dead(worker.pid)
    if ENV != "dev":
        # Force remove even if directory is not empty
        rmtree(PROMETHEUS_MULTIPROC_DIR, ignore_errors=True)
    logger.error(
        f"***** ERROR: Child worker exited., worker: {worker.pid} *****")


class Application(BaseApplication):
    def load_config(self):
        s = self.cfg.set
        s('bind', bind)
        s('workers', workers)
        s('keepalive', keepalive)
        s('timeout', timeout)
        s('preload_app', "true")
        s('worker_class', "uvicorn.workers.UvicornWorker")
        s('when_ready', when_ready)
        s('child_exit', child_exit)
        s('accesslog', "-")
        s('errorlog', "-")

    def load(self):
        if ENV != "dev":
            setup_sentry(dsn=sentry_dsn)
            instrument_app_metrics(app)
            # instrument_app_tracing(app, service_name=PROJECT_NAME)
            app.middleware("http")(add_trace_id)  # Register the middleware

        plugin_path = "plugins"
        for plugin in listdir(plugin_path):
            try:
                if "ds_store" in str(plugin).lower():
                    print("✅ ds_store observed skipping")
                else:
                    mod = importlib.import_module(f"{plugin_path}.{plugin}.routes")
                    app.include_router(mod.router)
                    logger.info(f"✅ Mounted plugin: {plugin}")
            except Exception as e:
                logger.error(f"❌ Failed to mount plugin {plugin}: {e}")
        return app


Application().run()
