from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload, undefer

from fanfan.application.common.id_provider import IdProvider
from fanfan.core.models.page import Page, Pagination
from fanfan.core.models.participant import UserFullParticipantDTO
from fanfan.infrastructure.db.models import Nomination, Participant, Vote


class GetParticipantsPage:
    def __init__(self, session: AsyncSession, id_provider: IdProvider) -> None:
        self.session = session
        self.id_provider = id_provider

    async def __call__(
        self,
        pagination: Pagination | None = None,
        nomination_id: str | None = None,
        search_query: str | None = None,
    ) -> Page[UserFullParticipantDTO]:
        query = (
            select(Participant)
            .order_by(Participant.scoped_id)
            .options(
                joinedload(Participant.event),
                joinedload(Participant.nomination),
                undefer(Participant.votes_count),
            )
        )
        total_query = select(func.count(Participant.id))

        if pagination:
            query = query.limit(pagination.limit).offset(pagination.offset)

        if nomination_id:
            query = query.where(
                Participant.nomination.has(Nomination.id == nomination_id),
            )
            total_query = total_query.where(
                Participant.nomination.has(Nomination.id == nomination_id),
            )

        if search_query:
            query = query.where(
                or_(
                    Participant.title.ilike(f"%{search_query}%"),
                    Participant.scoped_id == int(search_query)
                    if search_query.isnumeric()
                    else False,
                )
            )
            total_query = total_query.where(
                or_(
                    Participant.title.ilike(f"%{search_query}%"),
                    Participant.scoped_id == int(search_query)
                    if search_query.isnumeric()
                    else False,
                )
            )

        if self.id_provider.get_current_user_id():
            query = query.options(contains_eager(Participant.user_vote)).outerjoin(
                Vote,
                and_(
                    Vote.participant_id == Participant.id,
                    Vote.user_id == self.id_provider.get_current_user_id(),
                ),
            )

        participants = await self.session.scalars(query)
        total = await self.session.scalar(total_query)

        return Page(
            items=[p.to_user_full_dto() for p in participants],
            total=total,
        )
