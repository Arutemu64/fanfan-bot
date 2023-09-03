import operator
from typing import Any

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.input.text import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Column, Select, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, List
from sqlalchemy import func

from src.bot.dialogs import states
from src.bot.structures import UserRole
from src.bot.ui import strings
from src.db import Database
from src.db.models import User

USERNAME_INPUT_ID = "username_input"
USER_ROLE_PICKER_ID = "user_role_picker"


async def get_roles(**kwargs):
    return {
        "roles": [
            (UserRole.VISITOR, UserRole.get_role_name(UserRole.VISITOR)),
            (UserRole.HELPER, UserRole.get_role_name(UserRole.HELPER)),
            (UserRole.ORG, UserRole.get_role_name(UserRole.ORG)),
        ]
    }


async def show_user_editor(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    db: Database = dialog_manager.middleware_data["db"]
    username = data.replace("@", "")
    user = await db.user.get_by_where(func.lower(User.username) == username.lower())
    if user:
        dialog_manager.dialog_data["user_id"] = user.id
        await dialog_manager.switch_to(states.ORG.USER_EDITOR)
    else:
        await message.reply("Пользователь не найден")


async def get_user_info(dialog_manager: DialogManager, db: Database, **kwargs):
    user = await db.user.get(dialog_manager.dialog_data["user_id"])
    return {
        "user_info": [
            ("ID", user.id),
            ("Юзернейм", user.username),
            ("Роль", UserRole.get_role_name(user.role)),
        ]
    }


async def delete_user(callback: CallbackQuery, button: Button, manager: DialogManager):
    db: Database = manager.middleware_data["db"]
    user = await db.user.get(manager.dialog_data["user_id"])
    user_id, username = user.id, user.username
    await db.session.delete(user)
    await db.session.commit()
    await manager.bg(user_id=user_id).start(
        state=states.REGISTRATION.MAIN, mode=StartMode.RESET_STACK
    )
    await callback.answer(f"Пользователь @{username} удален!")
    await manager.switch_to(states.ORG.MAIN)


async def change_user_role(
    callback: CallbackQuery, widget: Any, manager: DialogManager, item_id: str
):
    db: Database = manager.middleware_data["db"]
    user = await db.user.get(manager.dialog_data["user_id"])
    user.role = item_id
    await db.session.commit()
    try:
        await callback.bot.send_message(
            chat_id=user.id, text="Ваша роль была изменена, перезапуск бота..."
        )
        await manager.bg(chat_id=user.id).start(
            state=states.MAIN.MAIN, mode=StartMode.RESET_STACK
        )
    except TelegramBadRequest:
        pass
    await callback.answer(f"Роль пользователя @{user.username} была изменена!")
    await manager.switch_to(states.ORG.USER_EDITOR)


ask_username_window = Window(
    Const("Введите @юзернейм пользователя:"),
    TextInput(
        id=USERNAME_INPUT_ID,
        type_factory=str,
        on_success=show_user_editor,
    ),
    SwitchTo(id="back", text=Const(strings.buttons.back), state=states.ORG.MAIN),
    state=states.ORG.ASK_USERNAME,
)

user_editor = Window(
    Const("<b>👤✏️ Редактирование пользователя</b>\n"),
    List(Format("{item[0]}: {item[1]}"), items="user_info"),
    SwitchTo(
        text=Const("Изменить роль пользователя"),
        id="change_user_role",
        state=states.ORG.CHANGE_ROLE,
    ),
    Button(
        id="delete_user", text=Const("❌ Удалить пользователя"), on_click=delete_user
    ),
    SwitchTo(id="back", text=Const(strings.buttons.back), state=states.ORG.MAIN),
    getter=get_user_info,
    state=states.ORG.USER_EDITOR,
)

changing_role_window = Window(
    Const("Выберите роль для пользователя:"),
    Column(
        Select(
            Format("{item[1]}"),
            id=USER_ROLE_PICKER_ID,
            item_id_getter=operator.itemgetter(0),
            items="roles",
            on_click=change_user_role,
        ),
    ),
    SwitchTo(id="back", text=Const(strings.buttons.back), state=states.ORG.USER_EDITOR),
    getter=get_roles,
    state=states.ORG.CHANGE_ROLE,
)
