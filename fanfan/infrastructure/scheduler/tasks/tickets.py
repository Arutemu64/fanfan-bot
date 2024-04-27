import asyncio
import logging
import math

from dishka import FromDishka
from dishka.integrations.taskiq import inject

from fanfan.application.exceptions.ticket import TicketAlreadyExist, TicketNotFound
from fanfan.application.services.ticket import TicketService
from fanfan.common.enums import UserRole
from fanfan.config import TimepadConfig
from fanfan.infrastructure.db import UnitOfWork
from fanfan.infrastructure.scheduler import broker
from fanfan.infrastructure.timepad.client import TimepadClient
from fanfan.infrastructure.timepad.models import OrderStatus

ORDERS_PER_REQUEST = 100
PARTICIPANT_NOMINATIONS = [
    "Участник сценической программы",
    "Участник не сценических конкурсов",
]

logger = logging.getLogger("__name__")


@broker.task(schedule=[{"cron": "0 * * * *"}], retry_on_error=True, max_retries=3)
@inject
async def update_tickets(
    client: FromDishka[TimepadClient],
    config: FromDishka[TimepadConfig],
    uow: FromDishka[UnitOfWork],
) -> None:
    if not (config.client_id or config.event_id):
        logger.info(
            "TimePad client id or event id was not provided, skipping importing"
        )
        return None
    added_tickets, deleted_tickets = 0, 0
    step = 0
    service = TicketService(uow)
    init = await client.get_orders(config.event_id)
    logger.info(f"Tickets import started, about to process {init.total} orders")
    while step != math.ceil(init.total / ORDERS_PER_REQUEST):
        orders = await client.get_orders(
            config.event_id, limit=ORDERS_PER_REQUEST, skip=step * ORDERS_PER_REQUEST
        )
        for order in orders.values:
            if order.status.name in [
                OrderStatus.PAID,
                OrderStatus.OK,
                OrderStatus.PAID_OFFLINE,
                OrderStatus.PAID_UR,
            ]:
                for ticket in order.tickets:
                    try:
                        await service.create_ticket(
                            ticket_id=ticket.number,
                            role=UserRole.PARTICIPANT
                            if ticket.ticket_type.name in PARTICIPANT_NOMINATIONS
                            else UserRole.VISITOR,
                        )
                        added_tickets += 1
                    except TicketAlreadyExist:
                        pass
            else:
                for ticket in order.tickets:
                    try:
                        await service.delete_ticket(ticket_id=ticket.number)
                        deleted_tickets += 1
                    except TicketNotFound:
                        pass
        logger.info(
            f"Ongoing import: {added_tickets} tickets added, {deleted_tickets} "
            f"tickets deleted"
        )
        await asyncio.sleep(3)
        step += 1
    logger.info(
        f"Import done: {added_tickets} tickets added, {deleted_tickets} tickets deleted"
    )
    return None
