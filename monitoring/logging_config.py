"""
AgentID — Structured Logging & Observability Setup

Import and call `setup_logging()` at app startup.
Import and call `setup_telemetry()` for OpenTelemetry tracing.
"""
import os
import logging
import sys
from typing import Optional


def setup_logging(level: Optional[str] = None) -> None:
    """Configure structured JSON logging for production, human-readable for dev."""
    log_level = level or os.getenv("LOG_LEVEL", "INFO")
    env = os.getenv("ENVIRONMENT", "development")

    if env == "development":
        fmt = "%(asctime)s %(levelname)-8s [%(name)s] %(message)s"
        logging.basicConfig(level=log_level, format=fmt, stream=sys.stdout)
    else:
        # JSON structured logging for production
        try:
            import json_log_formatter

            formatter = json_log_formatter.JSONFormatter()
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(formatter)
            logging.root.handlers = [handler]
            logging.root.setLevel(log_level)
        except ImportError:
            logging.basicConfig(level=log_level, stream=sys.stdout)
            logging.warning("json-log-formatter not installed, using basic logging")

    # Quiet noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def setup_telemetry() -> None:
    """Initialize OpenTelemetry tracing if endpoint is configured."""
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        logging.getLogger(__name__).info("OTEL endpoint not set, skipping telemetry")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanExporter
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        resource = Resource.create({
            "service.name": os.getenv("OTEL_SERVICE_NAME", "agentid-api"),
            "deployment.environment": os.getenv("ENVIRONMENT", "development"),
        })

        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=endpoint)
        provider.add_span_processor(BatchSpanExporter(exporter))
        trace.set_tracer_provider(provider)

        logging.getLogger(__name__).info(f"OpenTelemetry tracing enabled → {endpoint}")
    except ImportError:
        logging.getLogger(__name__).warning("OpenTelemetry packages not installed")


def setup_sentry() -> None:
    """Initialize Sentry error tracking if DSN is configured."""
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        return

    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

        sentry_sdk.init(
            dsn=dsn,
            environment=os.getenv("ENVIRONMENT", "development"),
            traces_sample_rate=0.1 if os.getenv("ENVIRONMENT") == "production" else 1.0,
            integrations=[FastApiIntegration(), SqlalchemyIntegration()],
        )
        logging.getLogger(__name__).info("Sentry error tracking enabled")
    except ImportError:
        logging.getLogger(__name__).warning("sentry-sdk not installed")
