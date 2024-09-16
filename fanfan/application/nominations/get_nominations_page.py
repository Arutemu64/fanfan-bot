from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager

from fanfan.application.common.id_provider import IdProvider
from fanfan.core.models.nomination import UserNominationDTO
from fanfan.core.models.page import Page, Pagination
from fanfan.infrastructure.db.models import Nomination, Participant, Vote


class GetNominationsPage:
    def __init__(self, session: AsyncSession, id_provider: IdProvider) -> None:
        self.session = session
        self.id_provider = id_provider

    async def __call__(
        self,
        pagination: Pagination | None = None,
    ) -> Page[UserNominationDTO]:
        query = select(Nomination)

        if pagination:
            query = query.limit(pagination.limit).offset(pagination.offset)

        if user_id := self.id_provider.get_current_user_id():
            query = query.options(contains_eager(Nomination.user_vote)).outerjoin(
                Vote,
                and_(
                    Vote.user_id == user_id,
                    Vote.participant.has(Participant.nomination_id == Nomination.id),
                ),
            )

        nominations = await self.session.scalars(query)
        total = await self.session.scalar(select(func.count(Nomination.id)))

        return Page(
            items=[n.to_user_dto() for n in nominations],
            total=total,
        )
