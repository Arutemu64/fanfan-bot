import logging
from dataclasses import dataclass

from fanfan.adapters.redis.repositories.mailing import MailingRepository
from fanfan.adapters.utils.events_broker import EventsBroker
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.core.dto.notification import UserNotification
from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.models.mailing import Mailing, MailingId
from fanfan.core.models.user import UserRole
from fanfan.presentation.stream.routes.notifications.send_to_roles import (
    SendNotificationToRolesDTO,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CreateRoleMailingDTO:
    text: str
    roles: list[UserRole]
    image_id: str | None = None


class CreateRoleMailing(Interactor[CreateRoleMailingDTO, Mailing]):
    def __init__(
        self,
        id_provider: IdProvider,
        mailing_repo: MailingRepository,
        stream_broker_adapter: EventsBroker,
    ):
        self.id_provider = id_provider
        self.mailing_repo = mailing_repo
        self.stream_broker_adapter = stream_broker_adapter

    async def __call__(self, data: CreateRoleMailingDTO) -> MailingId:
        sender = await self.id_provider.get_current_user()
        if sender.role is not UserRole.ORG:
            raise AccessDenied

        mailing_id = await self.mailing_repo.create_new_mailing(
            by_user_id=self.id_provider.get_current_user_id()
        )
        await self.stream_broker_adapter.send_to_roles(
            SendNotificationToRolesDTO(
                notification=UserNotification(
                    text=data.text,
                    bottom_text=f"Отправил @{sender.username}",
                    image_id=data.image_id,
                ),
                roles=data.roles,
                mailing_id=mailing_id,
            )
        )
        logger.info(
            "New roles mailing initiated by user %s",
            sender.id,
            extra={"mailing_id": mailing_id},
        )
        return mailing_id
