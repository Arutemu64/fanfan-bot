from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Nomination, Participant, Vote
from .abstract import Repository


class VoteRepo(Repository[Vote]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Vote, session=session)

    async def new(
        self,
        user_id: Optional[int] = None,
        participant_id: Optional[int] = None,
    ) -> Vote:
        new_vote = await self.session.merge(
            Vote(
                user_id=user_id,
                participant_id=participant_id,
            )
        )
        return new_vote

    async def get_user_vote(
        self,
        user_id: int,
        nomination_id: Optional[str] = None,
        participant_id: Optional[int] = None,
    ) -> Optional[Vote]:
        terms = [(Vote.user_id == user_id)]
        if nomination_id:
            terms.append(
                Vote.participant.has(Participant.nomination_id == nomination_id)
            )
        elif participant_id:
            terms.append(Vote.participant_id == participant_id)
        return await super()._get_by_where(query=and_(*terms))

    async def check_list_of_user_voted_nominations(
        self, user_id: int, nomination_ids: List[str]
    ) -> List[str]:
        stmt = select(Nomination.id).join(
            Vote,
            and_(
                Vote.user_id == user_id,
                Vote.participant.has(Participant.nomination_id == Nomination.id),
                Vote.participant.has(Participant.nomination_id.in_(nomination_ids)),
            ),
        )
        return [r[0] for r in (await self.session.execute(stmt)).all()]

    async def get_count(
        self, participant_id: Optional[int] = None, nomination_id: Optional[int] = None
    ) -> int:
        terms = []
        if participant_id:
            terms.append(Vote.participant_id == participant_id)
        elif nomination_id:
            terms.append(
                Vote.participant.has(Participant.nomination_id == nomination_id)
            )
        return await super()._get_count(query=and_(*terms))

    async def delete(self, vote_id: int):
        await super()._delete(Vote.id == vote_id)
