from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Settings
from .base import Repository


class SettingsRepo(Repository[Settings]):
    """
    User repository for CRUD and other SQL queries
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize user repository as for all users or only for one user
        """
        super().__init__(type_model=Settings, session=session)

    async def new(self):  # TODO
        return
