from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.application.common.id_provider import IdProvider
from fanfan.core.enums import UserRole
from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.notification import MailingInfo, UserNotification
from fanfan.infrastructure.db.models import User
from fanfan.infrastructure.scheduler.notifications.bot_notifier import Notifier


@dataclass
class CreateMailingDTO:
    text: str
    roles: list[UserRole]
    image_id: str | None = None


class CreateMailing:
    def __init__(
        self, session: AsyncSession, notifier: Notifier, id_provider: IdProvider
    ):
        self.session = session
        self.notifier = notifier
        self.id_provider = id_provider

    async def __call__(self, dto: CreateMailingDTO) -> MailingInfo:
        sender = await self.session.get(User, self.id_provider.get_current_user_id())
        if sender is None:
            raise UserNotFound
        if sender.role is not UserRole.ORG:
            raise AccessDenied
        users = await self.session.scalars(select(User).where(User.role.in_(dto.roles)))
        notifications = [
            UserNotification(
                user_id=u.id,
                text=dto.text,
                bottom_text=f"Отправил @{sender.username}",
                image_id=dto.image_id,
            )
            for u in users
        ]
        return await self.notifier.schedule_mailing(notifications)
