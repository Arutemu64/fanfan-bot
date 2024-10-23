from dishka import FromDishka
from faststream.nats import NatsBroker, NatsRouter, PullSub
from pydantic import BaseModel

from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.core.enums import UserRole
from fanfan.core.models.mailing import MailingId
from fanfan.core.models.notification import UserNotification
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
    users_dao: FromDishka[UsersRepository],
    mailing: FromDishka[MailingRepository],
    broker: FromDishka[NatsBroker],
) -> None:
    users = await users_dao.get_all_by_roles(*data.roles)
    for u in users:
        await broker.publish(
            SendNotificationDTO(
                user_id=u.id,
                notification=data.notification,
            ),
            subject=f"mailing.{data.mailing_id}",
        )
    await mailing.update_total(data.mailing_id, len(users))
    return
