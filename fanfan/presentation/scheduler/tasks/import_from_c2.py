from typing import Annotated

from dishka import FromDishka
from dishka.integrations.taskiq import inject
from taskiq import Context, TaskiqDepends

from fanfan.adapters.utils.stream_broker import StreamBrokerAdapter
from fanfan.application.utils.import_from_c2 import ImportFromC2, ImportFromC2Result
from fanfan.core.exceptions.base import AppException
from fanfan.core.models.notification import UserNotification
from fanfan.core.models.user import UserId
from fanfan.main.scheduler import broker
from fanfan.presentation.stream.routes.notifications.send_notification import (
    SendNotificationDTO,
)


@broker.task(task_name="import_from_c2")
@inject
async def import_from_c2(  # noqa: C901
    context: Annotated[Context, TaskiqDepends()],
    interactor: FromDishka[ImportFromC2],
    broker_adapter: FromDishka[StreamBrokerAdapter],
    by_user_id: UserId | None = None,
) -> ImportFromC2Result:
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
                        f"Было обработано {result.topics_merged} номинаций "
                        f"и {result.requests_merged} заявок. "
                        f"{len(result.failed_requests)} было пропущено. "
                        f"Было затрачено {result.elapsed_time} с.",
                    ),
                )
            )
        return result
