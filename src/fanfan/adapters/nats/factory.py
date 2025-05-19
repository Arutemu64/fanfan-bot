from typing import NewType

import nats
from nats.aio.client import Client

from fanfan.adapters.config.models import NatsConfig

NATSClient = NewType("NATSClient", Client)


async def create_nats_client(config: NatsConfig) -> NATSClient:
    return NATSClient(await nats.connect(config.build_connection_str()))
