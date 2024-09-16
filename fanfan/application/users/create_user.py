import logging
from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.core.enums import UserRole
from fanfan.core.exceptions.users import UserAlreadyExist
from fanfan.core.models.user import UserDTO
from fanfan.infrastructure.db.models import User

logger = logging.getLogger(__name__)


@dataclass
class CreateUserDTO:
    id: int
    username: str | None
    role: UserRole | None = UserRole.VISITOR


class CreateUser:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __call__(self, dto: CreateUserDTO) -> UserDTO:
        """Create a new user."""
        async with self.session:
            try:
                user = User(id=dto.id, username=dto.username, role=dto.role)
                self.session.add(user)
                await self.session.commit()
                logger.info("New user %s has registered", dto.id)
                return user.to_dto()
            except IntegrityError as e:
                await self.session.rollback()
                raise UserAlreadyExist from e
