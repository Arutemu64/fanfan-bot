from aiogram.enums import ContentType
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from dishka import AsyncContainer

from fanfan.application.marketplace.read_market import ReadMarket
from fanfan.application.marketplace.read_product import ReadProduct
from fanfan.core.models.user import UserData
from fanfan.core.vo.product import ProductId
from fanfan.presentation.tgbot.dialogs.marketplace.common import (
    DATA_SELECTED_PRODUCT_ID,
)


async def product_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    user: UserData,
    **kwargs,
):
    product_id = ProductId(dialog_manager.dialog_data[DATA_SELECTED_PRODUCT_ID])
    get_market: ReadMarket = await container.get(ReadMarket)
    get_product: ReadProduct = await container.get(ReadProduct)

    product = await get_product(product_id=product_id)
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
        "market_is_manager": user.id in (u.id for u in market.managers),
    }
