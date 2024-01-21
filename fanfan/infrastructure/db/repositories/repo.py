from typing import Generic, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Base

AbstractModel = TypeVar("AbstractModel", bound=Base)


class Repository(Generic[AbstractModel]):
    def __init__(self, type_model: Type[Base], session: AsyncSession):
        self.type_model = type_model
        self.session = session

    # async def update(self, id_: int, **kwargs) -> None:
    #     query = update(self.type_model).where(self.type_model.id == id_).values(kwargs)
    #     await self.session.execute(query)

    # async def add(self, dto) -> AbstractModel:
    #     ent = self._type_model(dto)
    #     self._session.add(ent)
    #     await self._session.flush()
    #     return ent

    # async def get(self, id_: int) -> AbstractModel:
    #     query = select(self._type_model).where(self._type_model.id == id_)
    #     return (await self._session.execute(query)).scalar_one_or_none()

    # async def _get_by_where(self, query) -> Optional[AbstractModel]:
    #     statement = select(self.type_model).where(query).limit(1)
    #     result = await self.session.execute(statement)
    #     return result.scalar_one_or_none()
    #
    # async def _get_many(
    #     self, query, limit: int, order_by=None
    # ) -> Sequence[AbstractModel]:
    #     statement = select(self.type_model).where(query).limit(limit)
    #     if order_by:
    #         statement = statement.order_by(order_by)
    #     result = await self.session.execute(statement)
    #     return result.scalars().all()
    #
    # async def _get_all(self, query, order_by=None) -> Sequence[AbstractModel]:
    #     statement = select(self.type_model).where(query)
    #     if order_by:
    #         statement = statement.order_by(order_by)
    #     result = await self.session.execute(statement)
    #     return result.scalars().all()
    #
    # async def _get_count(self, query=None) -> int:
    #     statement = select(func.count()).select_from(self.type_model)
    #     if query is not None:
    #         statement = statement.where(query)
    #     result = await self.session.execute(statement)
    #     return result.scalar()
    #
    # async def _paginate(
    #     self,
    #     page: int,
    #     items_per_page: int,
    #     query=None,
    #     order_by=None,
    #     options: Optional[List[ExecutableOption]] = None,
    # ) -> Sequence[AbstractModel]:
    #     statement = select(self.type_model)
    #     if query is not None:
    #         statement = statement.where(query)
    #     if order_by is not None:
    #         statement = statement.order_by(order_by)
    #     statement = statement.slice(
    #         page * items_per_page, (page * items_per_page) + items_per_page
    #     )
    #     if options is not None:
    #         statement = statement.options(*options)
    #     result = await self.session.execute(statement)
    #     return result.scalars().all()

    # @abc.abstractmethod
    # async def new(self, *args, **kwargs) -> None:
    #     """
    #     This method is need to be implemented in child classes,
    #     it is responsible for adding a new model to the database
    #     :return: Nothing
    #     """
    #     ...
