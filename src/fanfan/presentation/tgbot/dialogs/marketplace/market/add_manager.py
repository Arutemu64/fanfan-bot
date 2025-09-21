from aiogram.types import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.marketplace.update_market import UpdateMarket
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.utils import get_dialog_data_adapter
from fanfan.presentation.tgbot.dialogs.marketplace.data import (
    MarketDialogData,
)
from fanfan.presentation.tgbot.static import strings


@inject
async def add_manager_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
    update_market: FromDishka[UpdateMarket],
) -> None:
    dialog_data_adapter = get_dialog_data_adapter(dialog_manager)
    dialog_data = dialog_data_adapter.load(MarketDialogData)
    new_manager = await update_market.add_manager_by_username(
        market_id=dialog_data.market_id,
        username=data,
    )
    await message.answer(
        f"✅ <b>@{new_manager.username}</b> <i>({new_manager.id})</i> "
        f"стал новым управляющим магазина"
    )


add_manager_window = Window(
    Const(
        "💼 У магазина может быть несколько управляющих. "
        "Вы можете добавить знакомого человека, "
        "чтобы он мог помочь вам заполнить информацию или каталог магазина."
    ),
    Const(" "),
    Const(
        "⌨️ Для этого пришлите Telegram никнейм (без @, в любом регистре) "
        "нового управляющего магазина сообщением"
    ),
    Const(" "),
    Const("⚠️ Человек должен быть пользователем бота."),
    Const(
        "⚠️ Для удаления управляющего обратитесь к организаторам, "
        "не добавляйте посторонних людей в управляющие."
    ),
    TextInput(
        id="add_manager_username_input",
        on_success=add_manager_handler,
    ),
    SwitchTo(
        Const(strings.buttons.back), state=states.Marketplace.VIEW_MARKET, id="back"
    ),
    state=states.Marketplace.ADD_MANAGER,
)
