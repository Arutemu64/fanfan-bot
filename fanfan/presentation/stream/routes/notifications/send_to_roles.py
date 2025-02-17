from dishka import FromDishka
from faststream.nats import NatsRouter, PullSub
from pydantic import BaseModel

from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.adapters.utils.stream_broker import StreamBrokerAdapter
from fanfan.core.dto.notification import UserNotification
from fanfan.core.models.mailing import MailingId
from fanfan.core.models.user import UserRole
from fanfan.presentation.stream.jstream import stream
from fanfan.presentation.stream.routes.notifications.send_notification import (
    SendNotificationDTO,
)

router = NatsRouter()


class SendNotificationToRolesDTO(BaseModel):
    notification: UserNotification
    roles: list[UserRole]
    mailing_id: MailingId


@router.subscriber(
    "send_to_roles",
    stream=stream,
    pull_sub=PullSub(),
    durable="send_to_roles",
)
async def send_to_roles(
    data: SendNotificationToRolesDTO,
    users_repo: FromDishka[UsersRepository],
    mailing: FromDishka[MailingRepository],
    broker_adapter: FromDishka[StreamBrokerAdapter],
) -> None:
    users = await users_repo.get_all_by_roles(*data.roles)
    for u in users:
        await broker_adapter.send_notification(
            SendNotificationDTO(
                user_id=u.id,
                notification=data.notification,
            ),
            mailing_id=data.mailing_id,
        )
    await mailing.update_total(data.mailing_id, len(users))
    return
