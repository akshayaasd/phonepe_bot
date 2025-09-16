# gnani_sdk/middleware.py
from fastapi import Request
from opentelemetry.trace import get_current_span

async def add_trace_id(request: Request, call_next):
    response = await call_next(request)
    span = get_current_span()
    if span is not None:
        span_context = span.get_span_context()
        if span_context and span_context.trace_id:
            trace_id_hex = format(span_context.trace_id, '032x')  # 32-char hex
            response.headers["X-Trace-ID"] = trace_id_hex
    return response