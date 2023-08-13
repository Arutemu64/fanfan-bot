import operator
from typing import Any

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.input.text import ManagedTextInputAdapter
from aiogram_dialog.widgets.kbd import Button, Select, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, Jinja

from src.bot.dialogs import states
from src.bot.structures import Role
from src.bot.ui import strings
from src.db import Database
from src.db.models import User

USERNAME_INPUT_ID = "username_input"
USER_ROLE_PICKER_ID = "user_role_picker"


async def get_roles(**kwargs):
    roles = [
        ("Зритель", Role.VISITOR),
        ("Волонтёр", Role.HELPER),
        ("Организатор", Role.ORG),
    ]
    return {"roles": roles}


async def show_user_editor(
    message: Message,
    widget: ManagedTextInputAdapter,
    dialog_manager: DialogManager,
    data: str,
):
    db: Database = dialog_manager.middleware_data["db"]
    username = data.replace("@", "")
    user = await db.user.get_by_where(User.username == username)
    if user:
        dialog_manager.dialog_data["username"] = username
        await dialog_manager.switch_to(states.ORG.USER_EDITOR)
    else:
        await message.reply("Пользователь не найден")


async def get_user_info(dialog_manager: DialogManager, db: Database, **kwargs):
    username = dialog_manager.dialog_data["username"]
    user = await db.user.get_by_where(User.username == username)
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
    }


async def delete_user(callback: CallbackQuery, button: Button, manager: DialogManager):
    db: Database = manager.middleware_data["db"]
    username = manager.dialog_data["username"]
    user = await db.user.get_by_where(User.username == username)
    user_id = user.id
    # await db.session.execute(user.votes.delete())
    # await db.session.execute(user.issued_tickets.delete())
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
    username = manager.dialog_data["username"]
    user = await db.user.get_by_where(User.username == username)
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
    await callback.answer(f"Роль пользователя @{username} была изменена!")
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

# fmt: off
UserInfo = Jinja("ID: {{ id }}\n"
                 "Юзернейм: @{{ username }}\n"
                 "Роль: {{ role }}\n")
# fmt: on

user_editor = Window(
    Const("<b>👤✏️ Редактирование пользователя</b>\n"),
    UserInfo,
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
    Select(
        Format("{item[0]}"),
        id=USER_ROLE_PICKER_ID,
        item_id_getter=operator.itemgetter(1),
        items="roles",
        on_click=change_user_role,
    ),
    SwitchTo(id="back", text=Const(strings.buttons.back), state=states.ORG.USER_EDITOR),
    getter=get_roles,
    state=states.ORG.CHANGE_ROLE,
)
