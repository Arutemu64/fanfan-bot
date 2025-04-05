from __future__ import annotations

import typing

from faststream.nats import NatsBroker  # noqa: TCH002

from fanfan.core.models.schedule_change import ScheduleChange

if typing.TYPE_CHECKING:
    from fanfan.core.models.mailing import MailingId
    from fanfan.presentation.stream.routes.notifications.edit_notification import (
        EditNotificationDTO,
    )
    from fanfan.presentation.stream.routes.notifications.send_feedback_notifications import (  # noqa: E501
        SendFeedbackNotificationsDTO,
    )
    from fanfan.presentation.stream.routes.notifications.send_notification import (
        NewNotificationDTO,
    )
    from fanfan.presentation.stream.routes.notifications.send_to_roles import (
        SendNotificationToRolesDTO,
    )


class EventsBroker:
    def __init__(self, broker: NatsBroker):
        self.broker = broker

    async def send_to_roles(self, data: SendNotificationToRolesDTO) -> None:
        await self.broker.publish(data, subject="send_to_roles")

    async def cancel_mailing(self, mailing_id: MailingId) -> None:
        await self.broker.publish(mailing_id, subject="cancel_mailing")

    async def new_notification(
        self, data: NewNotificationDTO, mailing_id: MailingId | None = None
    ) -> None:
        if mailing_id:
            await self.broker.publish(
                data, subject=f"notifications.mailing.{mailing_id}"
            )
        else:
            await self.broker.publish(data, subject="notifications.new")

    async def edit_notification(self, data: EditNotificationDTO) -> None:
        await self.broker.publish(data, subject="edit_notification")

    async def schedule_changed(self, data: ScheduleChange):
        await self.broker.publish(data, subject="schedule.change.new")

    async def send_feedback_notifications(
        self, data: SendFeedbackNotificationsDTO
    ) -> None:
        await self.broker.publish(data, subject="send_feedback_notifications")
