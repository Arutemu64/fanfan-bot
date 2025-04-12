from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import CodeORM
from fanfan.core.models.code import Code, CodeId
from fanfan.core.models.user import UserId


class CodesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_code(self, model: Code) -> Code:
        code = CodeORM.from_model(model)
        self.session.add(code)
        await self.session.flush([code])
        return code.to_model()

    async def get_code_by_id(self, code_id: CodeId) -> Code | None:
        code = await self.session.get(CodeORM, code_id)
        return code.to_model() if code else None

    async def get_code_by_user(self, user_id: UserId) -> Code | None:
        query = select(CodeORM).where(CodeORM.user_id == user_id).limit(1)
        code = await self.session.scalar(query)
        return code.to_model() if code else None
