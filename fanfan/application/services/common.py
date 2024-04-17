from typing import Optional

from fanfan.application.services.base import BaseService


class CommonService(BaseService):
    async def get_random_quote(self) -> Optional[str]:
        return await self.uow.quotes.get_random_quote()
