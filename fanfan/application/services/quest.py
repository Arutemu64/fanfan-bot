from sqlalchemy.exc import IntegrityError

from fanfan.application.dto.achievement import FullAchievementDTO
from fanfan.application.dto.common import Page, UserNotification
from fanfan.application.dto.user import UserStats
from fanfan.application.exceptions.quest import (
    AchievementNotFound,
    UserAlreadyHasThisAchievement,
)
from fanfan.application.exceptions.users import (
    UserHasNoTicket,
    UserNotFound,
)
from fanfan.application.services.access import check_permission
from fanfan.application.services.base import BaseService
from fanfan.common.enums import UserRole
from fanfan.infrastructure.db.models import Transaction
from fanfan.infrastructure.scheduler import send_notification


class QuestService(BaseService):
    async def get_user_stats(self, user_id: int) -> UserStats:
        user = await self.uow.users.get_user_by_id(user_id)
        if not user:
            raise UserNotFound
        return await self.uow.users.get_user_stats(user_id)

    async def get_achievements_page(
        self, page_number: int, achievements_per_page: int, user_id: int
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

    @staticmethod
    def _points_pluralize(points: int) -> str:
        if (points % 10 == 1) and (points % 100 != 11):
            return "очков"
        elif (2 <= points % 10 <= 4) and (points % 100 < 10 or points % 100 >= 20):
            return "очка"
        else:
            return "очков"

    @check_permission(allowed_roles=[UserRole.HELPER, UserRole.ORG])
    async def add_points(self, user_id: int, amount: int) -> None:
        async with self.uow:
            user = await self.uow.users.get_user_by_id(user_id)
            if not user:
                raise UserHasNoTicket
            if not user.ticket:
                raise UserHasNoTicket

            user.points += amount
            transaction = Transaction(
                from_user_id=self.identity.id,
                to_user=user,
                points_added=amount,
            )
            self.uow.session.add(transaction)
            await self.uow.commit()

            await send_notification.kiq(
                UserNotification(
                    user_id=user.id,
                    text=f"💰 Вы получили "
                    f"{amount} {self._points_pluralize(amount)}!",
                )
            )

    @check_permission(allowed_roles=[UserRole.HELPER, UserRole.ORG])
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
                transaction = Transaction(
                    from_user_id=self.identity.id,
                    to_user=user,
                    achievement_added=achievement,
                )
                self.uow.session.add(transaction)
                await self.uow.commit()
            except IntegrityError:
                await self.uow.rollback()
                raise UserAlreadyHasThisAchievement

        await send_notification.kiq(
            UserNotification(
                user_id=user.id,
                text=f"🏆 Вы получили достижение <b>{achievement.title}</b>!",
            )
        )
