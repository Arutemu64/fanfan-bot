import asyncio
import logging
import math

from dishka import FromDishka
from dishka.integrations.taskiq import inject

from fanfan.application.tickets.create_ticket import CreateTicket, CreateTicketDTO
from fanfan.application.tickets.delete_ticket import DeleteTicket
from fanfan.common.config import TimepadConfig
from fanfan.core.enums import UserRole
from fanfan.core.exceptions.tickets import TicketAlreadyExist
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
    create_ticket: FromDishka[CreateTicket],
    delete_ticket: FromDishka[DeleteTicket],
) -> None:
    if not (config.client_id or config.event_id):
        logger.info(
            "TimePad client id or event id was not provided, skipping importing",
        )
        return
    added_tickets, deleted_tickets = 0, 0
    step = 0
    init = await client.get_orders(config.event_id)
    logger.info("Tickets import started, about to process %s orders", init.total)
    while step != math.ceil(init.total / ORDERS_PER_REQUEST):
        logger.info(
            "Ongoing import: %s tickets added, %s tickets deleted",
            added_tickets,
            deleted_tickets,
        )
        orders = await client.get_orders(
            config.event_id,
            limit=ORDERS_PER_REQUEST,
            skip=step * ORDERS_PER_REQUEST,
        )
        for order in orders.values:  # noqa: PD011
            if order.status.name in [
                OrderStatus.PAID,
                OrderStatus.OK,
                OrderStatus.PAID_OFFLINE,
                OrderStatus.PAID_UR,
            ]:
                for ticket in order.tickets:
                    try:
                        await create_ticket(
                            CreateTicketDTO(
                                id=ticket.number,
                                role=UserRole.PARTICIPANT
                                if ticket.ticket_type.name in PARTICIPANT_NOMINATIONS
                                else UserRole.VISITOR,
                            ),
                        )
                        added_tickets += 1
                    except TicketAlreadyExist:
                        pass
            else:
                for ticket in order.tickets:
                    await delete_ticket(ticket_id=ticket.number)
                    deleted_tickets += 1

        await asyncio.sleep(3)
        step += 1
    logger.info(
        "Import done: %s tickets added, %s tickets deleted",
        added_tickets,
        deleted_tickets,
    )
    return
