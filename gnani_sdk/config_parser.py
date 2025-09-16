import os
import configparser

ini_file_name = "config.ini"
config = configparser.ConfigParser(strict=True)
config.read(ini_file_name)

base_section = "base"
gunicorn_section = "gunicorn"
sentry_section = "sentry"
project_section = "project"
tracing_section = "tracing"
mongodb_section = "mongodb"
redis_section = "redis"

PRODUCTION = True if "PRODUCTION" in os.environ else False

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
assert LOG_LEVEL, "LOG_LEVEL not proper."

PROMETHEUS_METRICS_PORT = int(os.getenv(
    'PROMETHEUS_METRICS_PORT',
    int(config[gunicorn_section]["prometheus_metrics_port"])
))
assert PROMETHEUS_METRICS_PORT, f"PROMETHEUS_METRICS_PORT not set."

GUNICORN_REQUEST_KEEPALIVE = int(os.getenv(
    "GUNICORN_REQUEST_KEEPALIVE",
    int(config[gunicorn_section]["keepalive"])
))
assert GUNICORN_REQUEST_KEEPALIVE, f"GUNICORN_REQUEST_KEEPALIVE not set."

GUNICORN_REQUEST_TIMEOUT = int(os.getenv(
    "GUNICORN_REQUEST_TIMEOUT",
    int(config[gunicorn_section]["timeout"])
))
assert GUNICORN_REQUEST_TIMEOUT, f"GUNICORN_REQUEST_TIMEOUT not set."

SENTRY_DSN = os.getenv("SENTRY_DSN", config[sentry_section]["sentry_dsn"])
assert SENTRY_DSN, f"SENTRY_DSN not set."

SERVER_PORT = int(os.getenv("SERVER_PORT", config[base_section]["server_port"]))
assert SERVER_PORT, f"SERVER_PORT not set."

SERVER_WORKERS = int(os.getenv("SERVER_WORKERS", config[base_section]["server_workers"]))
assert SERVER_WORKERS, f"SERVER_WORKERS not set."

PROMETHEUS_MULTIPROC_DIR = os.getenv("PROMETHEUS_MULTIPROC_DIR", config[gunicorn_section]["prometheus_multiproc_dir"])
assert PROMETHEUS_MULTIPROC_DIR, f"PROMETHEUS_MULTIPROC_DIR not set."

PROJECT_NAME = os.getenv("PROJECT_NAME", config[project_section]["name"])
assert PROJECT_NAME, f"PROJECT_NAME not set."

JAEGER_ENDPOINT = os.getenv("JAEGER_ENDPOINT", config[tracing_section]["jaeger_endpoint"])
assert JAEGER_ENDPOINT, f"JAEGER_ENDPOINT not set."

ENV = os.getenv("ENV", config[base_section]["env"])
assert ENV, f"ENV not set."

MONGO_API_URL = os.getenv("MONGO_API_URL", config.get(mongodb_section, "mongo_api_url"))
MONGO_API_PORT = os.getenv("MONGO_API_PORT", config.get(mongodb_section, "mongo_api_port"))
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", config.get(mongodb_section, "mongo_db_name"))
MONGO_INPUT_COLLECTION = os.getenv("MONGO_INPUT_COLLECTION", config.get(mongodb_section, "mongo_input_collection"))
MONGO_OUTPUT_COLLECTION = os.getenv("MONGO_OUTPUT_COLLECTION", config.get(mongodb_section, "mongo_output_collection"))
MONGO_REJECT_COLLECTION = os.getenv("MONGO_REJECT_COLLECTION", config.get(mongodb_section, "mongo_reject_collection"))
MONGO_SMS_COLLECTION = os.getenv("MONGO_SMS_COLLECTION", config.get(mongodb_section, "mongo_sms_collection"))

REDIS_HOST = os.getenv("REDIS_HOST", config.get(redis_section, "redis_host"))
REDIS_PORT = os.getenv("REDIS_PORT", config.get(redis_section, "redis_port"))
REDIS_DB_NUMBER = os.getenv("REDIS_DB_NUMBER", config.get(redis_section, "redis_db_number"))