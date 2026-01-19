import logging
from dataclasses import dataclass

from fanfan.adapters.api.ticketscloud.client import TCloudClient
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.core.services.ticketscloud import TCloudService

logger = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE = 200


@dataclass(frozen=True, slots=True)
class SyncTCloudResult:
    new_tickets_count: int
    removed_tickets_count: int


class SyncTCloud:
    def __init__(
        self, client: TCloudClient, tcloud_service: TCloudService, uow: UnitOfWork
    ):
        self.client = client
        self.tcloud_service = tcloud_service
        self.uow = uow

    async def __call__(self) -> SyncTCloudResult:
        new_tickets_count, removed_tickets_count = 0, 0
        orders_init = await self.client.get_orders(page=1, page_size=DEFAULT_PAGE_SIZE)
        refunds_init = await self.client.get_refunds(
            page=1, page_size=DEFAULT_PAGE_SIZE
        )
        logger.info(
            "About to process %s orders and %s refunds from TicketsCloud",
            orders_init.total_count,
            refunds_init.total_count,
        )
        # Orders
        for page in range(1, orders_init.pagination.total + 1):
            result = await self.client.get_orders(
                page=page, page_size=DEFAULT_PAGE_SIZE
            )
            async with self.uow:
                for order_data in result.data:
                    new_tickets_count += await self.tcloud_service.proceed_order(
                        order_data
                    )
                await self.uow.commit()
                logger.info(
                    "Ongoing import: %s new tickets, %s removed tickets",
                    new_tickets_count,
                    removed_tickets_count,
                )
        # Refunds
        for page in range(1, refunds_init.pagination.total + 1):
            result = await self.client.get_refunds(
                page=page, page_size=DEFAULT_PAGE_SIZE
            )
            async with self.uow:
                for refunds_data in result.data:
                    removed_tickets_count += await self.tcloud_service.proceed_refund(
                        refunds_data
                    )
                await self.uow.commit()
                logger.info(
                    "Ongoing import: %s new tickets, %s removed tickets",
                    new_tickets_count,
                    removed_tickets_count,
                )
        return SyncTCloudResult(new_tickets_count, removed_tickets_count)
