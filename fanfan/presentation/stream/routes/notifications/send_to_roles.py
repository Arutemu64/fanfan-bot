from dishka import FromDishka
from dishka.integrations.faststream import inject
from faststream.nats import NatsRouter, PullSub

from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.adapters.utils.events_broker import EventsBroker
from fanfan.core.events.notifications import (
    NewNotificationEvent,
    NewRolesNotificationEvent,
)
from fanfan.presentation.stream.jstream import stream

router = NatsRouter()


@router.subscriber(
    "notifications.roles.new",
    stream=stream,
    pull_sub=PullSub(),
    durable="notifications_roles_new",
)
@inject
async def send_to_roles(
    data: NewRolesNotificationEvent,
    users_repo: FromDishka[UsersRepository],
    mailing: FromDishka[MailingRepository],
    broker_adapter: FromDishka[EventsBroker],
) -> None:
    users = await users_repo.get_all_by_roles(*data.roles)
    for u in users:
        await broker_adapter.publish(
            NewNotificationEvent(
                user_id=u.id,
                notification=data.notification,
                mailing_id=data.mailing_id,
            )
        )
    await mailing.update_total(data.mailing_id, len(users))
    return
