from dishka import FromDishka
from faststream.nats import NatsBroker, NatsRouter, PullSub
from pydantic import BaseModel

from fanfan.core.enums import UserRole
from fanfan.core.models.mailing import MailingId
from fanfan.core.models.notification import UserNotification
from fanfan.infrastructure.db.repositories.users import UsersRepository
from fanfan.infrastructure.redis.repositories.mailing import MailingRepository
from fanfan.infrastructure.stream.routes.send_notification import (
    SendNotificationDTO,
)
from fanfan.infrastructure.stream.stream import stream

router = NatsRouter()


class SendNotificationToRolesDTO(BaseModel):
    notification: UserNotification
    roles: list[UserRole]
    mailing_id: MailingId


@router.subscriber("send_to_roles", stream=stream, pull_sub=PullSub())
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
