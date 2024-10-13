import logging
from dataclasses import dataclass

from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.application.common.notifier import Notifier
from fanfan.core.enums import UserRole
from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.models.mailing import MailingData
from fanfan.core.models.notification import UserNotification

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CreateMailingDTO:
    text: str
    roles: list[UserRole]
    image_id: str | None = None


class CreateRoleMailing(Interactor[CreateMailingDTO, MailingData]):
    def __init__(self, notifier: Notifier, id_provider: IdProvider):
        self.notifier = notifier
        self.id_provider = id_provider

    async def __call__(self, data: CreateMailingDTO) -> MailingData:
        sender = await self.id_provider.get_current_user()
        if sender.role is not UserRole.ORG:
            raise AccessDenied

        mailing_data = await self.notifier.send_to_roles(
            notification=UserNotification(
                text=data.text,
                bottom_text=f"Отправил @{sender.username}",
                image_id=data.image_id,
            ),
            roles=data.roles,
        )
        logger.info(
            "New roles mailing initiated by user %s",
            sender.id,
            extra={"mailing_data": mailing_data},
        )
        return mailing_data
