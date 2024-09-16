import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.core.exceptions.achievements import (
    AchievementNotFound,
    UserAlreadyHasThisAchievement,
)
from fanfan.core.exceptions.users import TicketNotLinked, UserNotFound
from fanfan.core.models.notification import UserNotification
from fanfan.infrastructure.db.models import Achievement, User
from fanfan.infrastructure.scheduler.notifications.bot_notifier import Notifier

logger = logging.getLogger(__name__)


class AddAchievementToUser:
    def __init__(
        self,
        session: AsyncSession,
        notifier: Notifier,
    ) -> None:
        self.session = session
        self.notifier = notifier

    async def __call__(self, achievement_id: int, user_id: int) -> None:
        async with self.session:
            user = await self.session.get(
                User, user_id, options=[joinedload(User.ticket)]
            )
            if not user:
                raise UserNotFound
            if not user.ticket:
                raise TicketNotLinked

            achievement = await self.session.get(Achievement, achievement_id)
            if not achievement:
                raise AchievementNotFound

            try:
                user.received_achievements.add(achievement)
                await self.session.commit()
                logger.info("User %s received achievement %s", user_id, achievement_id)
                await self.notifier.send_notification(
                    UserNotification(
                        user_id=user.id,
                        text=f"🏆 Ты получил достижение <b>{achievement.title}</b>!",
                    ),
                )
            except IntegrityError as e:
                await self.session.rollback()
                raise UserAlreadyHasThisAchievement from e
