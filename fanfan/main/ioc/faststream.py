from typing import NewType

import nats
from dishka import Provider, Scope, provide
from faststream.nats import NatsBroker
from nats.aio.client import Client
from nats.js import JetStreamContext

from fanfan.adapters.config.models import NatsConfig
from fanfan.adapters.utils.stream_broker import StreamBrokerAdapter
from fanfan.presentation.stream.broker import create_broker

NATS = NewType("NATS", Client)


class FastStreamProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_broker(self, config: NatsConfig) -> NatsBroker:
        broker = create_broker(config=config)
        await broker.connect()
        return broker

    broker_adapter = provide(StreamBrokerAdapter)

    @provide
    async def get_nc(self, config: NatsConfig) -> NATS:
        return NATS(await nats.connect(config.build_connection_str()))

    @provide
    async def get_jetstream(self, nc: NATS) -> JetStreamContext:
        return nc.jetstream()
