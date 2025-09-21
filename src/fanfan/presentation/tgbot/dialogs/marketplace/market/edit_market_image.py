from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.marketplace.update_market import UpdateMarket
from fanfan.core.vo.telegram import TelegramFileId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.utils import get_dialog_data_adapter
from fanfan.presentation.tgbot.dialogs.marketplace.data import (
    MarketDialogData,
)
from fanfan.presentation.tgbot.dialogs.marketplace.market.common import market_getter
from fanfan.presentation.tgbot.static import strings


@inject
async def new_market_image_handler(
    message: Message,
    message_input: MessageInput,
    manager: DialogManager,
    update_market: FromDishka[UpdateMarket],
):
    dialog_data_adapter = get_dialog_data_adapter(manager)
    dialog_data = dialog_data_adapter.load(MarketDialogData)
    if message.photo:
        await update_market.update_image_id(
            market_id=dialog_data.market_id,
            image_id=TelegramFileId(message.photo[-1].file_id),
        )


@inject
async def delete_market_image_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    update_market: FromDishka[UpdateMarket],
):
    dialog_data_adapter = get_dialog_data_adapter(manager)
    dialog_data = dialog_data_adapter.load(MarketDialogData)
    await update_market.update_image_id(
        market_id=dialog_data.market_id,
        image_id=None,
    )


edit_market_image_window = Window(
    DynamicMedia(
        selector="market_image",
        when="market_image",
    ),
    Const("🖼️ Отправьте новое изображение магазина сообщением"),
    MessageInput(new_market_image_handler, content_types=[ContentType.PHOTO]),
    Button(
        Const("🗑️ Удалить изображение"),
        id="delete_market_image",
        when="market_image",
        on_click=delete_market_image_handler,
    ),
    SwitchTo(
        Const(strings.buttons.back), state=states.Marketplace.VIEW_MARKET, id="back"
    ),
    state=states.Marketplace.EDIT_MARKET_IMAGE,
    getter=market_getter,
)
