import math
from typing import Generic, List, Optional, Sequence, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.interfaces import ORMOption
from sqlalchemy.sql.base import ExecutableOption

from ...bot.structures import Page
from ..models import Base

AbstractModel = TypeVar("AbstractModel")


class Repository(Generic[AbstractModel]):
    """Repository abstract class"""

    type_model: Type[Base]
    session: AsyncSession

    def __init__(self, type_model: Type[Base], session: AsyncSession):
        self.type_model = type_model
        self.session = session

    async def _get(
        self,
        ident: int | str,
        options: Optional[Sequence[ORMOption]] = None,
    ) -> Optional[AbstractModel]:
        return await self.session.get(
            entity=self.type_model,
            ident=ident,
            options=options,
        )

    async def _get_by_where(
        self,
        query,
    ) -> Optional[AbstractModel]:
        statement = select(self.type_model).where(query).limit(1)
        return (await self.session.execute(statement)).scalar_one_or_none()

    async def _get_many(
        self,
        query=None,
        limit: Optional[int] = None,
        order_by=None,
        options: Optional[List[ExecutableOption]] = None,
    ) -> List[AbstractModel]:
        statement = select(self.type_model)
        if options:
            statement = statement.options(*options)
        if query is not None:
            statement = statement.where(query)
        if limit:
            statement = statement.limit(limit)
        if order_by:
            statement = statement.order_by(order_by)
        return (await self.session.execute(statement)).scalars().all()

    async def _get_range(
        self,
        start: int,
        end: int,
        query=None,
        order_by=None,
        options: Optional[List[ExecutableOption]] = None,
    ) -> List[AbstractModel]:
        statement = select(self.type_model)
        if options:
            statement = statement.options(*options)
        if query is not None:
            statement = statement.where(query)
        if order_by:
            statement = statement.order_by(order_by)
        statement = statement.slice(start, end)
        return (await self.session.execute(statement)).scalars().all()

    async def _get_count(self, query=None) -> int:
        statement = select(func.count()).select_from(self.type_model)
        if query is not None:
            statement = statement.where(query)
        return (await self.session.execute(statement)).scalar()

    async def _paginate(
        self,
        page: int,
        items_per_page: int,
        query=None,
        order_by=None,
        options: Optional[List[ExecutableOption]] = None,
    ) -> Page[AbstractModel]:
        items = await self._get_range(
            start=(page * items_per_page),
            end=(page * items_per_page) + items_per_page,
            query=query,
            order_by=order_by,
            options=options,
        )
        total = math.ceil(await self._get_count(query) / items_per_page)
        return Page(
            items=items,
            number=page,
            total=total if total > 0 else 1,
        )

    # @abc.abstractmethod
    # async def new(self, *args, **kwargs) -> None:
    #     """
    #     This method is need to be implemented in child classes,
    #     it is responsible for adding a new model to the database
    #     :return: Nothing
    #     """
    #     ...
