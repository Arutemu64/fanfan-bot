from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import Feedback
from fanfan.core.models.feedback import FeedbackModel


class FeedbackRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_feedback(self, model: FeedbackModel) -> FeedbackModel:
        feedback = Feedback(user_id=model.user_id, text=model.text, asap=model.asap)
        self.session.add(feedback)
        await self.session.flush([feedback])
        return feedback.to_model()