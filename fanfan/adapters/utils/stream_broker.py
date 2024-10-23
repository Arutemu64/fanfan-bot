from faststream.nats import NatsBroker

from fanfan.core.models.mailing import MailingId
from fanfan.presentation.stream.routes.notifications.send_announcements import (
    SendAnnouncementsDTO,
)
from fanfan.presentation.stream.routes.notifications.send_notification import (
    SendNotificationDTO,
)
from fanfan.presentation.stream.routes.notifications.send_to_roles import (
    SendNotificationToRolesDTO,
)


class StreamBrokerAdapter:
    def __init__(self, broker: NatsBroker):
        self.broker = broker

    async def send_to_roles(self, data: SendNotificationToRolesDTO) -> None:
        await self.broker.publish(data, subject="send_to_roles")

    async def delete_mailing(self, mailing_id: MailingId) -> None:
        await self.broker.publish(mailing_id, subject="delete_mailing")

    async def send_notification(self, dto: SendNotificationDTO) -> None:
        await self.broker.publish(dto, subject="send_notification")

    async def send_announcements(self, data: SendAnnouncementsDTO) -> None:
        await self.broker.publish(data, subject="send_announcements")
