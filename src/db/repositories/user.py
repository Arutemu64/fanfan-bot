from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.structures import UserRole

from ..models import User
from .base import Repository


class UserRepo(Repository[User]):
    """
    User repository for CRUD and other SQL queries
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize user repository as for all users or only for one user
        """
        super().__init__(type_model=User, session=session)

    async def new(
        self,
        id: int = None,
        username: str = None,
        role: str = UserRole.VISITOR,
    ) -> User:
        new_user = await self.session.merge(
            User(
                id=id,
                username=username,
                role=role,
            )
        )
        return new_user
