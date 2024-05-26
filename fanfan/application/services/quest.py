import logging

from sqlalchemy.exc import IntegrityError

from fanfan.application.dto.achievement import FullAchievementDTO
from fanfan.application.dto.common import Page
from fanfan.application.dto.notification import UserNotification
from fanfan.application.dto.user import UserStats
from fanfan.application.exceptions.quest import (
    AchievementNotFound,
    UserAlreadyHasThisAchievement,
)
from fanfan.application.exceptions.users import (
    UserHasNoTicket,
    UserNotFound,
)
from fanfan.application.services.base import BaseService
from fanfan.infrastructure.scheduler.tasks.notifications import send_notification

logger = logging.getLogger(__name__)


class QuestService(BaseService):
    async def get_user_stats(self, user_id: int) -> UserStats:
        user = await self.uow.users.get_user_by_id(user_id)
        if not user:
            raise UserNotFound
        return await self.uow.users.get_user_stats(user_id)

    async def get_achievements_page(
        self,
        page_number: int,
        achievements_per_page: int,
        user_id: int,
    ) -> Page[FullAchievementDTO]:
        return await self.uow.achievements.paginate_achievements(
            page_number=page_number,
            achievements_per_page=achievements_per_page,
            user_id=user_id,
        )

    async def add_achievement(self, user_id: int, achievement_id: int):
        user = await self.uow.users.get_user_by_id(user_id)
        if not user:
            raise UserNotFound
        if not user.ticket:
            raise UserHasNoTicket
        achievement = await self.uow.achievements.get_achievement(achievement_id)
        if not achievement:
            raise AchievementNotFound

        async with self.uow:
            try:
                await self.uow.achievements.add_achievement_to_user(
                    achievement_id=achievement_id,
                    user_id=user_id,
                )
                await self.uow.commit()
                logger.info(
                    f"User id={user_id} received achievement id={achievement_id}"
                )
            except IntegrityError:
                await self.uow.rollback()
                raise UserAlreadyHasThisAchievement

        await send_notification.kiq(
            UserNotification(
                user_id=user.id,
                text=f"🏆 Ты получил достижение <b>{achievement.title}</b>!",
            ),
        )
