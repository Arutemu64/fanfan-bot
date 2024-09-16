from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.core.exceptions.participants import ParticipantNotFound
from fanfan.core.models.participant import ParticipantDTO
from fanfan.infrastructure.db.models import Participant


class GetParticipantByScopedId:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __call__(self, nomination_id: str, scoped_id: int) -> ParticipantDTO:
        participant = await self.session.scalar(
            select(Participant)
            .where(
                and_(
                    Participant.nomination_id == nomination_id,
                    Participant.scoped_id == scoped_id,
                ),
            )
            .limit(1)
        )
        if participant:
            return participant.to_dto()
        raise ParticipantNotFound
