from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.structures import Role

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
        ticket_id: str,
        tg_id: int = None,
        username: str = None,
        role: str = Role.VISITOR,
    ) -> User:
        new_ticket = await self.session.merge(
            User(
                ticket_id=ticket_id,
                tg_id=tg_id,
                username=username,
                role=role,
            )
        )
        return new_ticket
