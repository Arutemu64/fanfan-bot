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
from fanfan.infrastructure.scheduler import send_notification


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
        page = await self.uow.achievements.paginate_achievements(
            page_number=page_number,
            achievements_per_page=achievements_per_page,
            user_id=user_id,
        )
        return Page(
            items=[a.to_full_dto() for a in page.items],
            number=page.number,
            total_pages=page.total_pages if page.total_pages > 0 else 1,
        )

    async def add_achievement(self, user_id: int, achievement_id: int):
        user = await self.uow.users.get_user_by_id(user_id)
        if not user:
            raise UserNotFound
        if not user.ticket:
            raise UserHasNoTicket
        achievement = await self.uow.achievements.get_achievement(achievement_id)
        if not achievement:
            raise AchievementNotFound(achievement_id)

        async with self.uow:
            try:
                user.received_achievements.add(achievement)
                await self.uow.commit()
            except IntegrityError:
                await self.uow.rollback()
                raise UserAlreadyHasThisAchievement

        await send_notification.kiq(
            UserNotification(
                user_id=user.id,
                text=f"🏆 Вы получили достижение <b>{achievement.title}</b>!",
            ),
        )
