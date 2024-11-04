from __future__ import annotations

from typing import TYPE_CHECKING

from fanfan.core.models.mailing import MailingId
from fanfan.presentation.stream.routes.notifications.edit_notification import (
    EditNotificationDTO,
)
from fanfan.presentation.stream.routes.notifications.send_announcements import (
    SendAnnouncementsDTO,
)
from fanfan.presentation.stream.routes.notifications.send_feedback_notifications import (  # noqa: E501
    SendFeedbackNotificationsDTO,
)
from fanfan.presentation.stream.routes.notifications.send_notification import (
    SendNotificationDTO,
)
from fanfan.presentation.stream.routes.notifications.send_to_roles import (
    SendNotificationToRolesDTO,
)

if TYPE_CHECKING:
    from faststream.nats import NatsBroker


class StreamBrokerAdapter:
    def __init__(self, broker: NatsBroker):
        self.broker = broker

    async def send_to_roles(self, data: SendNotificationToRolesDTO) -> None:
        await self.broker.publish(data, subject="send_to_roles")

    async def delete_mailing(self, mailing_id: MailingId) -> None:
        await self.broker.publish(mailing_id, subject="delete_mailing")

    async def send_notification(
        self, data: SendNotificationDTO, mailing_id: MailingId | None = None
    ) -> None:
        if mailing_id:
            await self.broker.publish(data, subject=f"mailing.{mailing_id}")
        else:
            await self.broker.publish(data, subject="send_notification")

    async def edit_notification(self, data: EditNotificationDTO):
        await self.broker.publish(data, subject="edit_notification")

    async def send_announcements(self, data: SendAnnouncementsDTO) -> None:
        await self.broker.publish(data, subject="send_announcements")

    async def send_feedback_notifications(self, data: SendFeedbackNotificationsDTO):
        await self.broker.publish(data, subject="send_feedback_notifications")
