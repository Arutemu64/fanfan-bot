import asyncio
import logging
import math
import time
from dataclasses import dataclass
from datetime import timedelta

from fanfan.adapters.api.timepad.client import TimepadClient
from fanfan.adapters.api.timepad.exceptions import NoTimepadConfigProvided
from fanfan.adapters.config.models import TimepadConfig
from fanfan.adapters.utils.rate_lock import RateLockFactory
from fanfan.application.utils.proceed_order import (
    ProceedOrder,
)

logger = logging.getLogger(__name__)

ORDERS_PER_REQUEST = 100
SLEEP = 3

# Limits
IMPORT_ORDERS_LIMIT_NAME = "import_orders"
IMPORT_ORDERS_LIMIT_TIMEOUT = timedelta(minutes=30).seconds


@dataclass(slots=True, frozen=True)
class ImportOrdersResult:
    added_tickets: int
    deleted_tickets: int
    elapsed_time: int


class ImportOrders:
    def __init__(
        self,
        config: TimepadConfig | None,
        client: TimepadClient | None,
        rate_limit_factory: RateLockFactory,
        proceed_order: ProceedOrder,
    ):
        self.config = config
        self.client = client
        self.rate_limit_factory = rate_limit_factory
        self.proceed_order = proceed_order

    async def __call__(self) -> ImportOrdersResult:
        lock = self.rate_limit_factory(
            limit_name=IMPORT_ORDERS_LIMIT_NAME,
            cooldown_period=IMPORT_ORDERS_LIMIT_TIMEOUT,
            blocking=False,
            lock_timeout=timedelta(minutes=10).seconds,
        )
        async with lock:
            if self.client is None:
                raise NoTimepadConfigProvided
            added_tickets, deleted_tickets, step = 0, 0, 0
            init = await self.client.get_orders(self.config.event_id)
            logger.info(
                "Tickets import started, about to process %s orders", init.total
            )
            start = time.time()
            while step != math.ceil(init.total / ORDERS_PER_REQUEST):
                orders = await self.client.get_orders(
                    self.config.event_id,
                    limit=ORDERS_PER_REQUEST,
                    skip=step * ORDERS_PER_REQUEST,
                )
                for order in orders.values:  # noqa: PD011
                    result = await self.proceed_order(order)
                    added_tickets += result.added_tickets
                    deleted_tickets += result.deleted_tickets
                await asyncio.sleep(SLEEP)
                step += 1
                logger.info(
                    "Ongoing import: %s tickets added, %s tickets deleted",
                    added_tickets,
                    deleted_tickets,
                )
            end = time.time()
            result = ImportOrdersResult(
                added_tickets=added_tickets,
                deleted_tickets=deleted_tickets,
                elapsed_time=int(end - start),
            )
            logger.info(
                "Import done: %s tickets added, %s tickets deleted, elapsed time %s s",
                result.added_tickets,
                result.deleted_tickets,
                result.elapsed_time,
            )
            return result
