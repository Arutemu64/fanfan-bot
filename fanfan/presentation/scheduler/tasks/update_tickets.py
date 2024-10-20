import asyncio
import logging
import math
import time
from dataclasses import dataclass
from datetime import timedelta
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.taskiq import inject
from redis.asyncio import Redis
from taskiq import Context, TaskiqDepends

from fanfan.adapters.config_reader import TimepadConfig
from fanfan.adapters.timepad.client import TimepadClient
from fanfan.adapters.timepad.models import OrderStatus
from fanfan.application.common.notifier import Notifier
from fanfan.application.tickets.create_ticket import CreateTicket, CreateTicketDTO
from fanfan.application.tickets.delete_ticket import DeleteTicket
from fanfan.core.enums import UserRole
from fanfan.core.exceptions.base import AppException
from fanfan.core.exceptions.tasks import (
    NoTimepadConfigProvided,
    TaskInProgress,
    TooFast,
)
from fanfan.core.exceptions.tickets import TicketAlreadyExist, TicketNotFound
from fanfan.core.models.notification import SendNotificationDTO, UserNotification
from fanfan.core.models.ticket import TicketId
from fanfan.core.models.user import UserId
from fanfan.main.scheduler import broker

UPDATE_TICKETS_LOCK = "tasks:update_tickets:lock"
UPDATE_TICKETS_TIMESTAMP = "tasks:update_tickets:timestamp"
UPDATE_TICKETS_TIMEOUT = timedelta(minutes=30)

ORDERS_PER_REQUEST = 100
PARTICIPANT_NOMINATIONS = [
    "Участник сценической программы",
    "Участник не сценических конкурсов",
]

logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class UpdateTicketsResult:
    added_tickets: int
    deleted_tickets: int


@broker.task(task_name="update_tickets")
@inject
async def update_tickets(  # noqa: C901
    context: Annotated[Context, TaskiqDepends()],
    notifier: FromDishka[Notifier],
    redis: FromDishka[Redis],
    client: FromDishka[TimepadClient],
    config: FromDishka[TimepadConfig],
    create_ticket: FromDishka[CreateTicket],
    delete_ticket: FromDishka[DeleteTicket],
    by_user_id: UserId | None = None,
) -> UpdateTicketsResult:
    lock = redis.lock(UPDATE_TICKETS_LOCK, timeout=timedelta(minutes=5).seconds)
    try:
        # Check Timepad config
        if not (config.client_id or config.event_id):
            raise NoTimepadConfigProvided  # noqa: TRY301
        # Acquire lock
        if await lock.acquire(blocking=False) is False:
            raise TaskInProgress  # noqa: TRY301
        # Check timeout
        timestamp = float(await redis.get(UPDATE_TICKETS_TIMESTAMP) or 0)
        if (time.time() - timestamp) < UPDATE_TICKETS_TIMEOUT.seconds:
            raise TooFast  # noqa: TRY301
        added_tickets, deleted_tickets, step = 0, 0, 0
        init = await client.get_orders(config.event_id)
        logger.info("Tickets import started, about to process %s orders", init.total)
        while step != math.ceil(init.total / ORDERS_PER_REQUEST):
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
                                    id=TicketId(ticket.number),
                                    role=UserRole.PARTICIPANT
                                    if ticket.ticket_type.name
                                    in PARTICIPANT_NOMINATIONS
                                    else UserRole.VISITOR,
                                ),
                            )
                            added_tickets += 1
                        except TicketAlreadyExist:
                            pass
                else:
                    for ticket in order.tickets:
                        try:
                            await delete_ticket(TicketId(ticket.number))
                            deleted_tickets += 1
                        except TicketNotFound:
                            pass
            await asyncio.sleep(3)
            step += 1
            logger.info(
                "Ongoing import: %s tickets added, %s tickets deleted",
                added_tickets,
                deleted_tickets,
            )
    except AppException as e:
        if by_user_id:
            await notifier.send_notification(
                SendNotificationDTO(
                    user_id=by_user_id,
                    notification=UserNotification(
                        text=e.message, title="⚙️⚠️ Ошибка выполнения задачи"
                    ),
                )
            )
        await lock.release()
        context.reject()
    except Exception as e:
        if by_user_id:
            await notifier.send_notification(
                SendNotificationDTO(
                    user_id=by_user_id,
                    notification=UserNotification(
                        text=e.__str__(), title="⚙️⚠️ Ошибка выполнения задачи"
                    ),
                )
            )
        await lock.release()
        raise
    else:
        result = UpdateTicketsResult(
            added_tickets=added_tickets, deleted_tickets=deleted_tickets
        )
        logger.info(
            "Import done: %s tickets added, %s tickets deleted",
            added_tickets,
            deleted_tickets,
        )
        if by_user_id:
            await notifier.send_notification(
                SendNotificationDTO(
                    user_id=by_user_id,
                    notification=UserNotification(
                        title="⚙️✅ Задача выполнена",
                        text=f"Обновление билетов завершено: было добавлено "
                        f"{result.added_tickets} новых билетов и удалено "
                        f"{result.deleted_tickets} билетов.",
                    ),
                )
            )
        await redis.set(UPDATE_TICKETS_TIMESTAMP, time.time())
        await lock.release()
        return result
