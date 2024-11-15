import sentry_sdk
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from fanfan.adapters.config_reader import Configuration

AioHttpClientInstrumentor().instrument()
RedisInstrumentor().instrument()


def setup_telemetry(service_name: str, config: Configuration) -> TracerProvider:
    # Setup Sentry
    if config.debug.sentry_enabled:
        sentry_sdk.init(
            dsn=config.debug.sentry_dsn,
            environment=config.env_name,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            instrumenter="otel",
        )

    # Setup OTLP
    resource = Resource.create(attributes={"service.name": service_name})
    tracer_provider = TracerProvider(resource=resource)
    if config.debug.otlp_endpoint:
        exporter = OTLPSpanExporter(
            endpoint=config.debug.otlp_endpoint.unicode_string()
        )
        processor = BatchSpanProcessor(exporter)
        tracer_provider.add_span_processor(processor)
    trace.set_tracer_provider(tracer_provider)
    return tracer_provider
