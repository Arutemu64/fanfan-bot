import prometheus_client
from faststream.nats import NatsBroker
from faststream.nats.opentelemetry import NatsTelemetryMiddleware
from faststream.nats.prometheus import NatsPrometheusMiddleware
from opentelemetry.trace import TracerProvider
from prometheus_client import CollectorRegistry

from fanfan.adapters.config_reader import NatsConfig
from fanfan.presentation.stream.routes import setup_router


def create_broker(
    config: NatsConfig,
    tracer_provider: TracerProvider | None = None,
    registry: CollectorRegistry = prometheus_client.REGISTRY,
) -> NatsBroker:
    broker = NatsBroker(config.build_connection_str())
    broker.include_router(setup_router())
    if tracer_provider:
        broker.add_middleware(NatsTelemetryMiddleware(tracer_provider=tracer_provider))
    if registry:
        broker.add_middleware(NatsPrometheusMiddleware(registry=registry))
    return broker
