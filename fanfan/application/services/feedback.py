from fanfan.application.dto.feedback import CreateFeedbackDTO
from fanfan.application.exceptions.access import AccessDenied
from fanfan.application.exceptions.users import UserNotFound
from fanfan.application.services.base import BaseService
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
                contact_agreement=dto.contact_agreement,
                asap=dto.asap,
            )
            self.uow.session.add(feedback)
            await self.uow.session.commit()
