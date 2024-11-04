import logging
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.taskiq import inject
from taskiq import Context, TaskiqDepends

from fanfan.adapters.utils.stream_broker import StreamBrokerAdapter
from fanfan.application.utils.import_orders import (
    ImportOrders,
    ImportOrdersResult,
)
from fanfan.core.dto.notification import UserNotification
from fanfan.core.exceptions.base import AppException
from fanfan.core.models.user import UserId
from fanfan.main.scheduler import broker
from fanfan.presentation.stream.routes.notifications.send_notification import (
    SendNotificationDTO,
)

logger = logging.getLogger(__name__)


@broker.task(task_name="import_orders")
@inject
async def import_orders(
    context: Annotated[Context, TaskiqDepends()],
    interactor: FromDishka[ImportOrders],
    broker_adapter: FromDishka[StreamBrokerAdapter],
    by_user_id: UserId | None = None,
) -> ImportOrdersResult:
    try:
        result = await interactor()
    except AppException as e:
        if by_user_id:
            await broker_adapter.send_notification(
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
            await broker_adapter.send_notification(
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
            await broker_adapter.send_notification(
                SendNotificationDTO(
                    user_id=by_user_id,
                    notification=UserNotification(
                        title="⚙️✅ Задача выполнена",
                        text=f"Обновление билетов завершено: было добавлено "
                        f"{result.added_tickets} новых билетов и удалено "
                        f"{result.deleted_tickets} билетов. "
                        f"Было затрачено {result.elapsed_time} с.",
                    ),
                )
            )
        return result
