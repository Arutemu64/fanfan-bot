from typing import NewType

import nats
from dishka import Provider, Scope, provide
from faststream.nats import NatsBroker
from nats.aio.client import Client
from nats.js import JetStreamContext

from fanfan.adapters.config_reader import NatsConfig
from fanfan.presentation.stream.routes import setup_router

NATS = NewType("NATS", Client)


class FastStreamProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_broker(self, config: NatsConfig) -> NatsBroker:
        broker = NatsBroker(config.build_connection_str())
        broker.include_router(setup_router())
        await broker.connect()
        return broker

    @provide
    async def get_nc(self, config: NatsConfig) -> NATS:
        return NATS(await nats.connect(config.build_connection_str()))

    @provide
    async def get_jetstream(self, nc: NATS) -> JetStreamContext:
        return nc.jetstream()