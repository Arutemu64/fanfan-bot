from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.core.enums import UserRole
from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.notification import UserNotification
from fanfan.infrastructure.db.models import Feedback, User
from fanfan.infrastructure.scheduler.notifications.bot_notifier import Notifier


@dataclass
class CreateFeedbackDTO:
    user_id: int
    text: str
    asap: bool


class SendFeedback:
    def __init__(
        self,
        session: AsyncSession,
        notifier: Notifier,
    ) -> None:
        self.session = session
        self.notifier = notifier

    async def __call__(self, dto: CreateFeedbackDTO) -> None:
        async with self.session:
            user = await self.session.get(
                User, dto.user_id, options=[joinedload(User.permissions)]
            )
            if not user:
                raise UserNotFound
            if not user.permissions.can_send_feedback:
                raise AccessDenied

            feedback = Feedback(user=user, text=dto.text, asap=dto.asap)
            self.session.add(feedback)
            await self.session.commit()
            if dto.asap:
                orgs = await self.session.scalars(
                    select(User).where(User.role.is_(UserRole.ORG))
                )
                notifications = [
                    UserNotification(
                        user_id=org.id,
                        title="💬 ОБРАТНАЯ СВЯЗЬ",
                        text=f"Поступила срочная обратная связь "
                        f"от @{user.username} ({user.id}):\n\n"
                        f"<i>{dto.text}</i>",
                        bottom_text="ограничить доступ пользователя к "
                        "обратной связи можно отключив "
                        "у него право can_send_feedback",
                    )
                    for org in orgs
                ]
                await self.notifier.schedule_mailing(notifications)
            return
