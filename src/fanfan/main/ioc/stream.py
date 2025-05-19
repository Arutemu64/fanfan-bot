from dishka import Provider, Scope, provide
from faststream.nats import NatsBroker
from nats.js import JetStreamContext

from fanfan.adapters.config.models import NatsConfig
from fanfan.adapters.nats.factory import NATSClient, create_nats_client
from fanfan.adapters.utils.events_broker import EventsBroker
from fanfan.presentation.stream.broker import create_broker
from fanfan.presentation.stream.jinja.factory import (
    StreamJinjaEnvironment,
    create_stream_jinja,
)


class StreamProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_broker(self, config: NatsConfig) -> NatsBroker:
        broker = create_broker(config=config)
        await broker.connect()
        return broker

    broker_adapter = provide(EventsBroker)

    @provide
    async def get_nats_client(self, config: NatsConfig) -> NATSClient:
        return await create_nats_client(config)

    @provide
    async def get_jetstream(self, nc: NATSClient) -> JetStreamContext:
        return nc.jetstream()

    @provide
    def get_stream_jinja_env(self) -> StreamJinjaEnvironment:
        return create_stream_jinja()
