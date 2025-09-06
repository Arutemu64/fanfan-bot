from faststream.nats import NatsRouter

from fanfan.presentation.stream.routes.notifications import (
    cancel_mailing,
    edit_notification,
    send_notification,
    send_to_roles,
)
from fanfan.presentation.stream.routes.schedule import process_schedule_change
from fanfan.presentation.stream.routes.voting import voting_contest


def setup_router() -> NatsRouter:
    router = NatsRouter()

    router.include_router(cancel_mailing.router)
    router.include_router(send_notification.router)
    router.include_router(send_to_roles.router)
    router.include_router(edit_notification.router)

    router.include_router(process_schedule_change.router)

    router.include_router(voting_contest.router)

    return router
