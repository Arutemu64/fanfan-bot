import logging
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.taskiq import inject
from taskiq import Context, TaskiqDepends

from fanfan.application.common.notifier import Notifier
from fanfan.application.utils.import_tickets import (
    ImportTickets,
    ImportTicketsResult,
)
from fanfan.core.exceptions.base import AppException
from fanfan.core.models.notification import SendNotificationDTO, UserNotification
from fanfan.core.models.user import UserId
from fanfan.main.scheduler import broker

logger = logging.getLogger(__name__)


@broker.task(task_name="import_tickets")
@inject
async def import_tickets(  # noqa: C901
    context: Annotated[Context, TaskiqDepends()],
    interactor: FromDishka[ImportTickets],
    notifier: FromDishka[Notifier],
    by_user_id: UserId | None = None,
) -> ImportTicketsResult:
    try:
        result = await interactor()
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
        raise
    else:
        if by_user_id:
            await notifier.send_notification(
                SendNotificationDTO(
                    user_id=by_user_id,
                    notification=UserNotification(
                        title="⚙️✅ Задача выполнена",
                        text=f"Обновление билетов завершено: было добавлено "
                        f"{result.added_tickets} новых билетов и удалено "
                        f"{result.deleted_tickets} билетов."
                        f"Было затрачено {result.elapsed_time} с.",
                    ),
                )
            )
        return result
