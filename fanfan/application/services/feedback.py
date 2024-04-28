from typing import List

from fanfan.application.dto.feedback import CreateFeedbackDTO
from fanfan.application.dto.notification import UserNotification
from fanfan.application.exceptions.access import AccessDenied
from fanfan.application.exceptions.users import UserNotFound
from fanfan.application.services.base import BaseService
from fanfan.application.services.notification import NotificationService
from fanfan.common.enums import UserRole
from fanfan.infrastructure.db.models import Feedback


class FeedbackService(BaseService):
    async def send_feedback(self, dto: CreateFeedbackDTO) -> None:
        user = await self.uow.users.get_user_by_id(dto.user_id)
        if not user:
            raise UserNotFound
        if not user.permissions.can_send_feedback:
            raise AccessDenied
        async with self.uow:
            feedback = Feedback(
                user_id=dto.user_id,
                text=dto.text,
                asap=dto.asap,
            )
            self.uow.session.add(feedback)
            await self.uow.session.commit()
            if dto.asap:
                notifications: List[UserNotification] = []
                for org in await self.uow.users.get_all_by_roles([UserRole.ORG]):
                    notifications.append(
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
                    )
                await NotificationService(self.uow, self.identity).send_notifications(
                    notifications
                )
            return
