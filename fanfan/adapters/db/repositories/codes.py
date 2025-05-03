from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import CodeORM
from fanfan.core.models.code import Code, CodeId
from fanfan.core.models.user import UserId


class CodesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_code(self, code: Code) -> Code:
        code_orm = CodeORM.from_model(code)
        self.session.add(code_orm)
        await self.session.flush([code_orm])
        return code_orm.to_model()

    async def get_code_by_id(self, code_id: CodeId) -> Code | None:
        stmt = select(CodeORM).where(CodeORM.id == code_id)
        code_orm = await self.session.scalar(stmt)
        return code_orm.to_model() if code_orm else None

    async def get_code_by_user_id(self, user_id: UserId) -> Code | None:
        stmt = select(CodeORM).where(CodeORM.user_id == user_id).limit(1)
        code_orm = await self.session.scalar(stmt)
        return code_orm.to_model() if code_orm else None
