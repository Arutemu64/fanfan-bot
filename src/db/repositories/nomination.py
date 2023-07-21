from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Nomination
from .base import Repository


class NominationRepo(Repository[Nomination]):
    """
    User repository for CRUD and other SQL queries
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize user repository as for all users or only for one user
        """
        super().__init__(type_model=Nomination, session=session)

    async def new(self):  # TODO
        return
