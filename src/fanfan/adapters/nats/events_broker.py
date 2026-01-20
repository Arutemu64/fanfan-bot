from faststream.nats import NatsBroker

from fanfan.core.events.base import AppEvent


class EventsBroker:
    def __init__(self, broker: NatsBroker):
        self.broker = broker

    async def publish(self, event: AppEvent):
        await self.broker.publish(event, subject=event.subject)
