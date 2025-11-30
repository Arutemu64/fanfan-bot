from faststream.nats import NatsBroker
from faststream.nats.opentelemetry import NatsTelemetryMiddleware

from fanfan.adapters.nats.config import NatsConfig


def create_broker(
    config: NatsConfig,
) -> NatsBroker:
    broker = NatsBroker(config.build_connection_str())
    broker.add_middleware(NatsTelemetryMiddleware())
    return broker
