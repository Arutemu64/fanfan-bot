from sqlalchemy.exc import IntegrityError

from fanfan.adapters.db.repositories.codes import CodesRepository
from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.code import Code
from fanfan.core.utils.code import generate_unique_code
from fanfan.core.vo.code import CodeId
from fanfan.core.vo.user import UserId


class GetUserCodeId:
    def __init__(
        self,
        codes_writer: CodesRepository,
        users_repo: UsersRepository,
        id_provider: IdProvider,
        uow: UnitOfWork,
    ):
        self.codes_repo = codes_writer
        self.users_repo = users_repo
        self.id_provider = id_provider
        self.uow = uow

    async def __call__(self, user_id: UserId) -> CodeId:
        user = await self.users_repo.get_user_by_id(user_id)
        if user is None:
            raise UserNotFound
        user_code = await self.codes_repo.get_code_by_user_id(user.id)
        if user_code is None:
            # Try to generate unique user code
            for _ in range(10):
                async with self.uow:
                    try:
                        user_code = Code(
                            id=CodeId(generate_unique_code()),
                            user_id=user_id,
                        )
                        await self.codes_repo.add_code(user_code)
                        await self.uow.commit()
                        break
                    except IntegrityError:
                        await self.uow.rollback()
        return user_code.id
