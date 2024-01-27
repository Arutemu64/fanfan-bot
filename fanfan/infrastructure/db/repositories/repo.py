from typing import Generic, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Base

AbstractModel = TypeVar("AbstractModel", bound=Base)


class Repository(Generic[AbstractModel]):
    def __init__(self, type_model: Type[Base], session: AsyncSession):
        self.type_model = type_model
        self.session = session
