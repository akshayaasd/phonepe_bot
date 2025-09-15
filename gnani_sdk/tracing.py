import sentry_sdk
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from gnani_sdk.config_parser import PROJECT_NAME, JAEGER_ENDPOINT

def setup_sentry(dsn):
    sentry_sdk.init(dsn=dsn, traces_sample_rate=1.0)


def setup_otel(service_name: str = "gnani-api"):
    trace.set_tracer_provider(
        TracerProvider(
            resource=Resource.create({SERVICE_NAME: service_name})
        )
    )

    tracer = trace.get_tracer_provider().get_tracer(__name__)

    otlp_exporter = OTLPSpanExporter(endpoint=JAEGER_ENDPOINT, insecure=True)
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

    return tracer

def instrument_app_tracing(app, service_name=PROJECT_NAME):
    setup_otel(service_name)
    FastAPIInstrumentor.instrument_app(app)