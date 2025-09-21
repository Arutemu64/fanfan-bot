from aiogram.enums import ContentType
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.marketplace.get_market_by_id import GetMarketById
from fanfan.core.dto.user import FullUserDTO
from fanfan.presentation.tgbot.dialogs.marketplace.data import MarketDialogData
from fanfan.presentation.tgbot.middlewares.dialog_data_adapter import DialogDataAdapter


@inject
async def market_getter(
    dialog_manager: DialogManager,
    current_user: FullUserDTO,
    dialog_data_adapter: DialogDataAdapter,
    get_market: FromDishka[GetMarketById],
    **kwargs,
):
    dialog_data = dialog_data_adapter.load(MarketDialogData)
    market = await get_market(market_id=dialog_data.market_id)
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
        "market_is_manager": current_user.id in (u.id for u in market.managers),
        "market_managers": market.managers,
    }
