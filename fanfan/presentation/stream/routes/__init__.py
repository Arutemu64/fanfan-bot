from faststream.nats import NatsRouter

from fanfan.presentation.stream.routes.notifications import (
    cancel_mailing,
    edit_notification,
    send_feedback_notifications,
    send_notification,
    send_to_roles,
)
from fanfan.presentation.stream.routes.schedule import send_announcements


def setup_router() -> NatsRouter:
    router = NatsRouter()

    router.include_router(cancel_mailing.router)
    router.include_router(send_notification.router)
    router.include_router(send_to_roles.router)
    router.include_router(edit_notification.router)
    router.include_router(send_feedback_notifications.router)

    router.include_router(send_announcements.router)

    return router
