import typing

from aiogram.types import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Cancel
from aiogram_dialog.widgets.text import Const

from fanfan.application.users.find_user_by_username import FindUserByUsername
from fanfan.application.users.get_user_by_id import GetUserById
from fanfan.core.exceptions.base import AppException
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.ui import strings

from .common import DATA_USER_ID

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer


async def search_user_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    container: AsyncContainer = dialog_manager.middleware_data["container"]
    get_user_by_id = await container.get(GetUserById)
    get_user_by_username = await container.get(FindUserByUsername)

    try:
        if data.isnumeric():
            user = await get_user_by_id(int(data))
        else:
            user = await get_user_by_username(data)
    except AppException as e:
        await message.answer(e.message)
        return

    await dialog_manager.start(states.UserManager.main, data={DATA_USER_ID: user.id})


search_user_window = Window(
    Const("⌨️ Напишите @никнейм или ID пользователя"),
    TextInput(
        id="manual_user_search_input",
        type_factory=str,
        on_success=search_user_handler,
    ),
    Cancel(id="back", text=Const(strings.buttons.back)),
    state=states.UserManager.search_user,
)
