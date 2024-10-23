from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import Feedback
from fanfan.core.models.feedback import FeedbackModel


class FeedbackRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_feedback(self, model: FeedbackModel) -> FeedbackModel:
        feedback = Feedback.from_model(model)
        self.session.add(feedback)
        await self.session.flush([feedback])
        return feedback.to_model()
