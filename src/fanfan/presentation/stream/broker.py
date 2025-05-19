from faststream.nats import NatsBroker
from faststream.nats.opentelemetry import NatsTelemetryMiddleware

from fanfan.adapters.config.models import NatsConfig
from fanfan.presentation.stream.routes import setup_router


def create_broker(
    config: NatsConfig,
) -> NatsBroker:
    broker = NatsBroker(config.build_connection_str())
    broker.include_router(setup_router())
    broker.add_middleware(NatsTelemetryMiddleware())
    return broker
