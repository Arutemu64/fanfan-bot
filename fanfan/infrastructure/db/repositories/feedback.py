from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.application.dto.feedback import CreateFeedbackDTO
from fanfan.infrastructure.db.models import Feedback
from fanfan.infrastructure.db.repositories.repo import Repository


class FeedbackRepository(Repository[Feedback]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=Feedback, session=session)

    async def add_feedback(self, dto: CreateFeedbackDTO) -> None:
        feedback = Feedback(**dto.model_dump(exclude_unset=True))
        self.session.add(feedback)
