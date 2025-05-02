from aiogram.enums import ContentType
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from dishka import AsyncContainer

from fanfan.application.marketplace.get_market import GetMarket
from fanfan.core.models.market import MarketId
from fanfan.core.models.user import UserFull
from fanfan.presentation.tgbot.dialogs.marketplace.common import DATA_SELECTED_MARKET_ID


async def market_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    user: UserFull,
    **kwargs,
):
    market_id = MarketId(dialog_manager.dialog_data[DATA_SELECTED_MARKET_ID])
    get_market: GetMarket = await container.get(GetMarket)

    market = await get_market(market_id=market_id)
    market_image = None
    if market.image_id:
        market_image = MediaAttachment(
            ContentType.PHOTO, file_id=MediaId(market.image_id)
        )

    return {
        "market_id": market.id,
        "market_name": market.name,
        "market_description": market.description,
        "market_image": market_image,
        "market_is_visible": market.is_visible,
        "market_is_manager": user in market.managers,
        "market_managers": market.managers,
    }
