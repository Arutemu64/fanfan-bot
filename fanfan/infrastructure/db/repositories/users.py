from typing import List, Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.common.enums import UserRole
from fanfan.infrastructure.db.repositories.repo import Repository

from ..models import Ticket, User


class UsersRepository(Repository[User]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=User, session=session)

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        return await self.session.get(User, user_id, options=[joinedload(User.ticket)])

    async def get_user_by_username(self, username: str) -> Optional[User]:
        query = (
            select(User)
            .where(func.lower(User.username) == username.lower().replace("@", ""))
            .limit(1)
        )
        query = query.options(joinedload(User.ticket))
        return await self.session.scalar(query)

    async def get_user_by_ticket(self, ticket_id: str) -> Optional[User]:
        query = (
            select(User)
            .where(User.ticket.has(func.lower(Ticket.id) == ticket_id.lower()))
            .limit(1)
        )
        query = query.options(joinedload(User.ticket))
        return await self.session.scalar(query)

    async def get_all_by_roles(self, roles: List[UserRole]) -> Sequence[User]:
        query = select(User).where(User.role.in_(roles))
        return (await self.session.scalars(query)).all()

    async def get_receive_all_announcements_users(self) -> Sequence[User]:
        query = select(User).where(User.receive_all_announcements.is_(True))
        return (await self.session.scalars(query)).all()
