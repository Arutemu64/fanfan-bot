import contextlib

from fanfan.adapters.api.cosplay2.client import Cosplay2Client
from fanfan.adapters.api.cosplay2.config import Cosplay2Config
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.core.exceptions.participants import (
    NonApprovedRequest,
    RequestHasNoVotingTitle,
)
from fanfan.core.services.cosplay2 import Cosplay2Service


class SyncCosplay2:
    def __init__(
        self,
        client: Cosplay2Client,
        config: Cosplay2Config,
        cosplay2_service: Cosplay2Service,
        uow: UnitOfWork,
    ):
        self.client = client
        self.config = config
        self.cosplay2_service = cosplay2_service
        self.uow = uow

    async def __call__(self):
        async with self.uow:
            # Sync topics
            topics = await self.client.get_topics_list()
            for topic in topics:
                await self.cosplay2_service.proceed_topic(topic)

            # Sync requests and values
            requests = await self.client.get_all_requests()
            values = await self.client.get_all_values()
            for request in requests:
                # Skip non-approved and no voting title requests
                with contextlib.suppress(RequestHasNoVotingTitle, NonApprovedRequest):
                    await self.cosplay2_service.proceed_request(request, values)

            await self.uow.commit()
