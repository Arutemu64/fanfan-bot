import typing

from aiogram.types import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Cancel
from aiogram_dialog.widgets.text import Const

from fanfan.application.users.get_user_by_id import GetUserById
from fanfan.application.users.read_user_by_username import ReadUserByUsername
from fanfan.core.vo.user import UserId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.user_manager import (
    DATA_USER_ID,
)
from fanfan.presentation.tgbot.static import strings

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer


async def manual_user_search_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    container: AsyncContainer = dialog_manager.middleware_data["container"]
    get_user_by_id: GetUserById = await container.get(GetUserById)
    get_user_by_username: ReadUserByUsername = await container.get(ReadUserByUsername)

    if data.isnumeric():
        user = await get_user_by_id(UserId(int(data)))
    else:
        user = await get_user_by_username(data)
    await dialog_manager.start(
        state=states.UserManager.USER_INFO,
        data={DATA_USER_ID: user.id},
    )


manual_user_search_window = Window(
    Const("⌨️ Напишите @никнейм или ID пользователя"),
    TextInput(
        id="manual_user_search_input",
        type_factory=str,
        on_success=manual_user_search_handler,
    ),
    Cancel(id="back", text=Const(strings.buttons.back)),
    state=states.UserManager.MANUAL_USER_SEARCH,
)
