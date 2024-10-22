from typing import Annotated

from dishka import FromDishka
from dishka.integrations.taskiq import inject
from taskiq import Context, TaskiqDepends

from fanfan.application.common.notifier import Notifier
from fanfan.application.utils.import_from_c2 import ImportFromC2, ImportFromC2Result
from fanfan.core.exceptions.base import AppException
from fanfan.core.models.notification import SendNotificationDTO, UserNotification
from fanfan.core.models.user import UserId
from fanfan.main.scheduler import broker


@broker.task(task_name="import_from_c2")
@inject
async def import_from_c2(  # noqa: C901
    context: Annotated[Context, TaskiqDepends()],
    interactor: FromDishka[ImportFromC2],
    notifier: FromDishka[Notifier],
    by_user_id: UserId | None = None,
) -> ImportFromC2Result:
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
                        f"Было обработано {result.topics_merged} номинаций "
                        f"и {result.requests_merged} заявок."
                        f"{result.requests_failed} было пропущено "
                        f"(см. логи для подробностей)",
                    ),
                )
            )
        return result
