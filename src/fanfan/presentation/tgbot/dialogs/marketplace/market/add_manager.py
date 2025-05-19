import typing

from aiogram.types import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const

from fanfan.application.marketplace.update_market import UpdateMarket
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.marketplace.common import DATA_SELECTED_MARKET_ID
from fanfan.presentation.tgbot.static import strings

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer


async def add_manager_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    container: AsyncContainer = dialog_manager.middleware_data["container"]
    update_market: UpdateMarket = await container.get(UpdateMarket)

    new_manager = await update_market.add_manager_by_username(
        market_id=dialog_manager.dialog_data[DATA_SELECTED_MARKET_ID],
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
