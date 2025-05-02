import typing

from aiogram.types import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja

from fanfan.application.marketplace.update_market import UpdateMarket
from fanfan.core.models.market import MAX_MARKET_NAME_LENGTH
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.marketplace.common import DATA_SELECTED_MARKET_ID
from fanfan.presentation.tgbot.dialogs.marketplace.market.common import market_getter
from fanfan.presentation.tgbot.static import strings

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer


async def edit_market_name_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    container: AsyncContainer = dialog_manager.middleware_data["container"]
    update_market: UpdateMarket = await container.get(UpdateMarket)

    await update_market.update_market_name(
        market_id=dialog_manager.dialog_data[DATA_SELECTED_MARKET_ID], new_name=data
    )

    await dialog_manager.switch_to(state=states.Marketplace.VIEW_MARKET)


edit_market_name_window = Window(
    Const(
        f"⌨️ Отправьте новое название магазина "
        f"(не более {MAX_MARKET_NAME_LENGTH} символов)"
    ),
    Const(" "),
    Jinja("Текущее название: <code>{{ market_name }}</code>"),
    TextInput(id="market_name_input", on_success=edit_market_name_handler),
    SwitchTo(
        Const(strings.buttons.back), state=states.Marketplace.VIEW_MARKET, id="back"
    ),
    state=states.Marketplace.EDIT_MARKET_NAME,
    getter=market_getter,
)
