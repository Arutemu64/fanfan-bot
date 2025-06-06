from fanfan.adapters.db.repositories.markets import MarketsRepository
from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.dto.user import UserDTO
from fanfan.core.exceptions.market import (
    MarketNotFound,
)
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.market import Market
from fanfan.core.services.market import MarketService
from fanfan.core.vo.market import MarketId
from fanfan.core.vo.telegram import TelegramFileId


class UpdateMarket:
    def __init__(
        self,
        markets_repo: MarketsRepository,
        users_repo: UsersRepository,
        id_provider: IdProvider,
        uow: UnitOfWork,
        service: MarketService,
    ):
        self.markets_repo = markets_repo
        self.users_repo = users_repo
        self.id_provider = id_provider
        self.uow = uow
        self.service = service

    async def _get_market(self, market_id: MarketId) -> Market:
        market = await self.markets_repo.get_market_by_id(market_id)
        if market is None:
            raise MarketNotFound
        user = await self.id_provider.get_user_data()
        self.service.ensure_user_can_manage_market(market=market, manager=user)
        return market

    async def update_market_name(self, market_id: MarketId, new_name: str) -> None:
        async with self.uow:
            market = await self._get_market(market_id)
            market.set_name(new_name)
            await self.markets_repo.save_market(market)
            await self.uow.commit()

    async def update_market_description(
        self, market_id: MarketId, new_description: str
    ) -> None:
        async with self.uow:
            market = await self._get_market(market_id)
            market.set_description(new_description)
            await self.markets_repo.save_market(market)
            await self.uow.commit()

    async def update_market_visibility(
        self, market_id: MarketId, is_visible: bool
    ) -> None:
        async with self.uow:
            market = await self._get_market(market_id)
            market.is_visible = is_visible
            await self.markets_repo.save_market(market)
            await self.uow.commit()

    async def update_image_id(
        self, market_id: MarketId, image_id: TelegramFileId | None
    ) -> None:
        async with self.uow:
            market = await self._get_market(market_id)
            market.image_id = image_id
            await self.markets_repo.save_market(market)
            await self.uow.commit()

    async def add_manager_by_username(
        self, market_id: MarketId, username: str
    ) -> UserDTO:
        async with self.uow:
            market = await self._get_market(market_id)
            user = await self.users_repo.read_user_by_username(username.lower())
            if user is None:
                raise UserNotFound
            market.add_manager(user.id)
            await self.markets_repo.save_market(market)
            await self.uow.commit()
            return user
