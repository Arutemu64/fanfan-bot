from aiogram_dialog import DialogManager

from fanfan.core.vo.market import MarketId
from fanfan.presentation.tgbot import states


async def open_market(manager: DialogManager, market_id: MarketId):
    await manager.start(
        state=states.Marketplace.VIEW_MARKET, data={"market_id": market_id}
    )
