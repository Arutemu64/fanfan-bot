import asyncio
import logging
import math
import time
from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy.exc import IntegrityError

from fanfan.adapters.config_reader import TimepadConfig
from fanfan.adapters.db.repositories.tickets import TicketsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.timepad.client import TimepadClient
from fanfan.adapters.timepad.exceptions import NoTimepadConfigProvided
from fanfan.adapters.timepad.schemas import OrderStatus
from fanfan.application.common.limiter import Limiter
from fanfan.core.enums import UserRole
from fanfan.core.models.ticket import TicketId, TicketModel

logger = logging.getLogger(__name__)

ORDERS_PER_REQUEST = 100
PARTICIPANT_NOMINATIONS = [
    "Участник сценической программы",
    "Участник не сценических конкурсов",
]
GOOD_STATUSES = [
    OrderStatus.PAID,
    OrderStatus.OK,
    OrderStatus.PAID_OFFLINE,
    OrderStatus.PAID_UR,
]
SLEEP = 3

# Limits
IMPORT_TICKETS_LIMIT_NAME = "import_tickets"
IMPORT_TICKETS_LIMIT_TIMEOUT = timedelta(minutes=30).seconds


@dataclass(slots=True, frozen=True)
class ImportTicketsResult:
    added_tickets: int
    deleted_tickets: int
    elapsed_time: int


class ImportTickets:
    def __init__(
        self,
        config: TimepadConfig,
        client: TimepadClient,
        tickets_repo: TicketsRepository,
        uow: UnitOfWork,
        limiter: Limiter,
    ):
        self.config = config
        self.client = client
        self.tickets_repo = tickets_repo
        self.uow = uow
        self.limiter = limiter

    async def __call__(self) -> ImportTicketsResult:
        async with self.limiter(
            limit_name=IMPORT_TICKETS_LIMIT_NAME,
            limit_timeout=IMPORT_TICKETS_LIMIT_TIMEOUT,
            blocking=False,
            lock_timeout=timedelta(minutes=10).seconds,
        ):
            if not (self.config.client_id or self.config.event_id):
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
                    if order.status.name in GOOD_STATUSES:
                        for ticket in order.tickets:
                            async with self.uow:
                                try:
                                    await self.tickets_repo.add_ticket(
                                        TicketModel(
                                            id=TicketId(ticket.number),
                                            role=UserRole.PARTICIPANT
                                            if ticket.ticket_type.name
                                            in PARTICIPANT_NOMINATIONS
                                            else UserRole.VISITOR,
                                            issued_by_id=None,
                                        )
                                    )
                                    await self.uow.commit()
                                    added_tickets += 1
                                except IntegrityError:
                                    await self.uow.rollback()
                    else:
                        for ticket in order.tickets:
                            check = await self.tickets_repo.get_ticket_by_id(
                                TicketId(ticket.number)
                            )
                            if check:
                                async with self.uow:
                                    await self.tickets_repo.delete_ticket(
                                        TicketId(ticket.number)
                                    )
                                    await self.uow.commit()
                                    deleted_tickets += 1
                await asyncio.sleep(SLEEP)
                step += 1
                logger.info(
                    "Ongoing import: %s tickets added, %s tickets deleted",
                    added_tickets,
                    deleted_tickets,
                )
            end = time.time()
            result = ImportTicketsResult(
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
