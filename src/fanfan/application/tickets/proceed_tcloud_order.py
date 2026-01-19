from dataclasses import dataclass

from fanfan.adapters.api.ticketscloud.dto.order import Order
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.core.services.ticketscloud import TCloudService


@dataclass(slots=True, frozen=True)
class TCloudWebhookDTO:
    data: Order
    type: str  # TODO Enforce possible types later


@dataclass(slots=True, frozen=True)
class ProceedTCloudWebhookResult:
    new_tickets_count: int


class ProceedTCloudWebhook:
    def __init__(self, tcloud_service: TCloudService, uow: UnitOfWork):
        self.tcloud_service = tcloud_service
        self.uow = uow

    async def __call__(self, data: TCloudWebhookDTO) -> ProceedTCloudWebhookResult:
        async with self.uow:
            new_tickets_count = await self.tcloud_service.proceed_order(data.data)
            await self.uow.commit()
            return ProceedTCloudWebhookResult(new_tickets_count=new_tickets_count)
