from aiogram.enums import ContentType
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.marketplace.get_market_by_id import GetMarketById
from fanfan.application.marketplace.get_product_by_id import GetProductById
from fanfan.core.dto.user import FullUserDTO
from fanfan.presentation.tgbot.dialogs.marketplace.data import (
    MarketDialogData,
)
from fanfan.presentation.tgbot.middlewares.dialog_data_adapter import DialogDataAdapter


@inject
async def product_getter(
    dialog_manager: DialogManager,
    current_user: FullUserDTO,
    dialog_data_adapter: DialogDataAdapter,
    get_market: FromDishka[GetMarketById],
    get_product: FromDishka[GetProductById],
    **kwargs,
):
    dialog_data = dialog_data_adapter.load(MarketDialogData)
    product = await get_product(product_id=dialog_data.product_id)
    market = await get_market(market_id=product.market_id)

    product_image = None
    if product.image_id:
        product_image = MediaAttachment(
            ContentType.PHOTO, file_id=MediaId(product.image_id)
        )

    return {
        "product_name": product.name,
        "product_description": product.description,
        "product_price": product.price,
        "product_image": product_image,
        # Don't use market_getter with product_getter
        # cause it uses market_id from dialog data, not from product
        "market_name": market.name,
        "market_is_manager": current_user.id in (u.id for u in market.managers),
    }
