from sqlalchemy import Select, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import NominationORM, ParticipantORM, VoteORM
from fanfan.core.dto.nomination import NominationUserDTO
from fanfan.core.dto.page import Pagination
from fanfan.core.models.nomination import Nomination
from fanfan.core.vo.nomination import NominationId
from fanfan.core.vo.user import UserId


def _select_nomination_user_dto(user_id: UserId | None) -> Select:
    return select(NominationORM, VoteORM).outerjoin(
        VoteORM,
        and_(
            VoteORM.user_id == user_id,
            VoteORM.participant.has(ParticipantORM.nomination_id == NominationORM.id),
        ),
    )


def _parse_nomination_user_dto(
    nomination: NominationORM, vote: VoteORM | None
) -> NominationUserDTO:
    return NominationUserDTO(
        id=nomination.id,
        title=nomination.title,
        vote_id=vote.id if vote else None,
    )


class NominationsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_nomination(self, nomination: Nomination) -> Nomination:
        nomination_orm = NominationORM.from_model(nomination)
        self.session.add(nomination_orm)
        await self.session.flush([nomination_orm])
        return nomination_orm.to_model()

    async def get_nomination_by_id(
        self, nomination_id: NominationId
    ) -> Nomination | None:
        stmt = (
            select(NominationORM)
            .where(NominationORM.id == nomination_id)
            .with_for_update()
        )
        nomination_orm = await self.session.scalar(stmt)
        return nomination_orm.to_model() if nomination_orm else None

    async def get_nomination_by_code(self, nomination_code: str) -> Nomination | None:
        stmt = (
            select(NominationORM)
            .where(NominationORM.code == nomination_code)
            .with_for_update()
        )
        nomination_orm = await self.session.scalar(stmt)
        return nomination_orm.to_model() if nomination_orm else None

    async def save_nomination(self, nomination: Nomination) -> Nomination:
        nomination_orm = await self.session.merge(NominationORM.from_model(nomination))
        await self.session.flush([nomination_orm])
        return nomination_orm.to_model()

    async def read_nomination(
        self, nomination_id: NominationId, user_id: UserId
    ) -> NominationUserDTO | None:
        stmt = _select_nomination_user_dto(user_id).where(
            NominationORM.id == nomination_id
        )

        result = (await self.session.execute(stmt)).first()

        if result:
            nomination_orm, vote_orm = result
            return _parse_nomination_user_dto(nomination=nomination_orm, vote=vote_orm)
        return None

    async def read_votable_nominations_for_user(
        self,
        user_id: UserId,
        pagination: Pagination | None = None,
    ) -> list[NominationUserDTO]:
        stmt = _select_nomination_user_dto(user_id).where(
            NominationORM.is_votable.is_(True)
        )

        if pagination:
            stmt = stmt.limit(pagination.limit).offset(pagination.offset)

        results = (await self.session.execute(stmt)).all()

        return [
            _parse_nomination_user_dto(nomination=nomination_orm, vote=vote_orm)
            for nomination_orm, vote_orm in results
        ]

    async def count_votable_nominations(self) -> int:
        stmt = select(func.count(NominationORM.id)).where(
            NominationORM.is_votable.is_(True)
        )
        return await self.session.scalar(stmt)
