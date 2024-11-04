from faststream.nats import NatsRouter

from fanfan.presentation.stream.routes.notifications import (
    delete_mailing,
    edit_notification,
    send_announcements,
    send_feedback_notifications,
    send_notification,
    send_to_roles,
)


def setup_router() -> NatsRouter:
    router = NatsRouter()

    router.include_router(delete_mailing.router)
    router.include_router(send_announcements.router)
    router.include_router(send_notification.router)
    router.include_router(send_to_roles.router)
    router.include_router(edit_notification.router)
    router.include_router(send_feedback_notifications.router)

    return router
