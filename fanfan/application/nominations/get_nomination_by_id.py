from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.nominations import NominationNotFound
from fanfan.core.models.nomination import UserNominationDTO
from fanfan.infrastructure.db.models import Nomination, Participant, Vote


class GetNominationById:
    def __init__(
        self,
        session: AsyncSession,
        id_provider: IdProvider,
    ) -> None:
        self.session = session
        self.id_provider = id_provider

    async def __call__(
        self,
        nomination_id: str,
    ) -> UserNominationDTO:
        query = select(Nomination).where(Nomination.id == nomination_id).limit(1)

        if user_id := self.id_provider.get_current_user_id():
            query = query.options(contains_eager(Nomination.user_vote)).outerjoin(
                Vote,
                and_(
                    Vote.user_id == user_id,
                    Vote.participant.has(Participant.nomination_id == Nomination.id),
                ),
            )

        if nomination := await self.session.scalar(query):
            return nomination.to_user_dto()
        raise NominationNotFound
