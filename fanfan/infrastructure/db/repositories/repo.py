import math
from typing import Generic, Type, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.application.dto.common import Page

from ..models import Base

AbstractModel = TypeVar("AbstractModel", bound=Base)


class Repository(Generic[AbstractModel]):
    def __init__(self, type_model: Type[Base], session: AsyncSession):
        self.type_model = type_model
        self.session = session

    async def _paginate(
        self,
        query: Select,
        page_number: int,
        items_per_page: int,
    ) -> Page[AbstractModel]:
        total_subquery = select(func.count(query.columns.id))
        if query.whereclause is not None:
            total_subquery = total_subquery.where(query.whereclause)
        total_subquery = total_subquery.label("total")
        query = query.add_columns(total_subquery).slice(
            start=(page_number * items_per_page),
            stop=(page_number * items_per_page) + items_per_page,
        )
        result = (await self.session.execute(query)).all()
        return Page(
            items=[x[0] for x in result],
            number=page_number,
            total_pages=math.ceil(result[0].total / items_per_page)
            if len(result) > 0
            else 0,
        )
