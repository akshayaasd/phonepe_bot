import logging
from gnani_sdk.config_parser import LOG_LEVEL
from opentelemetry.trace import get_current_span

class TraceIdInjectFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        span = get_current_span()
        trace_id = "N/A"
        if span:
            span_context = span.get_span_context()
            if span_context and span_context.trace_id:
                trace_id = format(span_context.trace_id, '032x')
        record.trace_id = trace_id
        return True

class SessionIdInjectFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, 'sender_id'):
            record.sender_id = None
        return True

def setup_logger(name="gnani"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] - %(levelname)s - %(name)s - trace_id=%(trace_id)s - sender_id=%(sender_id)s - %(process)d/%(thread)d - %(funcName)s:%(lineno)d - %(message)s'
        )
        handler.setFormatter(formatter)
        handler.addFilter(TraceIdInjectFilter())
        handler.addFilter(SessionIdInjectFilter())
        logger.addHandler(handler)
        logger.setLevel(LOG_LEVEL)
    return logger