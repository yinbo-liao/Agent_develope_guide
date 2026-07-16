from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any, Iterator

from app.core.config import settings

logger = logging.getLogger(__name__)

try:  # pragma: no cover - depends on local optional packages
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
except ModuleNotFoundError:  # pragma: no cover - graceful fallback
    trace = None
    OTLPSpanExporter = None
    FastAPIInstrumentor = None
    Resource = None
    TracerProvider = None
    BatchSpanProcessor = None


class TracingManager:
    def __init__(self) -> None:
        self.enabled = bool(
            settings.ENABLE_TRACING
            and trace
            and OTLPSpanExporter
            and FastAPIInstrumentor
            and Resource
            and TracerProvider
            and BatchSpanProcessor
        )
        self.tracer = None
        if not self.enabled:
            return

        resource = Resource.create({"service.name": "ai-workflow-platform"})
        provider = TracerProvider(resource=resource)
        provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(
                    endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
                    insecure=True,
                )
            )
        )
        trace.set_tracer_provider(provider)
        self.tracer = trace.get_tracer("ai-workflow-platform")

    def instrument_fastapi(self, app: Any) -> None:
        if not self.enabled or FastAPIInstrumentor is None:
            logger.info("Tracing disabled or optional dependencies unavailable")
            return
        FastAPIInstrumentor.instrument_app(app)

    @contextmanager
    def start_span(self, name: str, attributes: dict[str, Any] | None = None) -> Iterator[Any]:
        if not self.enabled or self.tracer is None:
            yield None
            return
        with self.tracer.start_as_current_span(name, attributes=attributes or {}) as span:
            yield span


tracing_manager = TracingManager()
