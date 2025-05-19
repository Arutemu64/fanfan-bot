from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import CodeORM
from fanfan.core.dto.code import CodeDTO
from fanfan.core.models.code import Code
from fanfan.core.vo.code import CodeId
from fanfan.core.vo.user import UserId


def _parse_code_dto(code_orm: CodeORM) -> CodeDTO:
    return CodeDTO(
        id=code_orm.id,
        achievement_id=code_orm.achievement_id,
        user_id=code_orm.user_id,
        ticket_id=code_orm.ticket_id,
    )


class CodesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_code(self, code: Code) -> Code:
        code_orm = CodeORM.from_model(code)
        self.session.add(code_orm)
        await self.session.flush([code_orm])
        return code_orm.to_model()

    async def get_code_by_user_id(self, user_id: UserId) -> Code | None:
        stmt = select(CodeORM).where(CodeORM.user_id == user_id).limit(1)
        code_orm = await self.session.scalar(stmt)
        return code_orm.to_model() if code_orm else None

    async def read_code_by_id(self, code_id: CodeId) -> CodeDTO | None:
        stmt = select(CodeORM).where(CodeORM.id == code_id)
        code_orm = await self.session.scalar(stmt)
        return _parse_code_dto(code_orm) if code_orm else None
