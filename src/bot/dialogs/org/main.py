import operator

import jwt
from aiogram.types import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.dialog import ChatEvent
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Cancel,
    Checkbox,
    Column,
    ManagedCheckbox,
    Radio,
    Start,
    SwitchTo,
    Url,
)
from aiogram_dialog.widgets.text import Const, Format

from src.bot.dialogs import states
from src.bot.dialogs.getters import get_roles
from src.bot.dialogs.widgets import Title
from src.bot.structures import UserRole
from src.bot.ui import strings
from src.config import conf
from src.db import Database

ID_TICKET_ROLE_PICKER = "ticket_role_picker"
ID_VOTING_ENABLED_CHECKBOX = "voting_enabled_checkbox"


async def org_menu_getter(dialog_manager: DialogManager, db: Database, **kwargs):
    await dialog_manager.find(ID_VOTING_ENABLED_CHECKBOX).set_checked(
        await db.settings.get_voting_enabled()
    )
    jwt_token = jwt.encode(
        payload={"user_id": dialog_manager.event.from_user.id},
        key=conf.web.secret_key,
        algorithm="HS256",
    )
    return {
        "web_panel_login_link": f"{conf.web.build_admin_auth_url()}?token={jwt_token}",
    }


async def switch_voting(
    event: ChatEvent, checkbox: ManagedCheckbox, manager: DialogManager
):
    db: Database = manager.middleware_data["db"]
    await db.settings.set_voting_enabled(
        manager.find(ID_VOTING_ENABLED_CHECKBOX).is_checked()
    )
    await db.session.commit()


async def add_new_ticket(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    db: Database = dialog_manager.middleware_data["db"]
    role = dialog_manager.find(ID_TICKET_ROLE_PICKER).get_checked()

    if await db.ticket.get(data):
        await message.reply("⚠️ Билет с таким номером уже существует!")
        return

    new_ticket = await db.ticket.new(
        id=data,
        role=UserRole(int(role)),
        issued_by=dialog_manager.middleware_data["current_user"],
    )
    await db.session.commit()

    await message.answer(
        f"""✅ Билет "{new_ticket.id}" с ролью {new_ticket.role} успешно добавлен!"""
    )
    await dialog_manager.switch_to(states.ORG.MAIN)


new_ticket_window = Window(
    Const("✔️ Отметьте роль для билета ниже и напишите его номер"),
    Column(
        Radio(
            Format("🔘 {item[1]}"),
            Format("⚪️ {item[1]}"),
            id=ID_TICKET_ROLE_PICKER,
            item_id_getter=operator.itemgetter(0),
            items="roles",
        ),
    ),
    TextInput(id="ticket_id", type_factory=str, on_success=add_new_ticket),
    SwitchTo(state=states.ORG.MAIN, id="org_menu", text=Const(strings.buttons.back)),
    getter=get_roles,
    state=states.ORG.NEW_TICKET,
)

org_menu = Window(
    Title(strings.titles.org_menu),
    Url(
        text=Const("🌐 Перейти в организатора"),
        url=Format("{web_panel_login_link}"),
    ),
    SwitchTo(
        state=states.ORG.CREATE_NOTIFICATION,
        id="new_notification",
        text=Const("✉️ Сделать рассылку"),
    ),
    Start(
        state=states.USER_MANAGER.MANUAL_USER_SEARCH,
        id="user_search",
        text=Const("🔍 Найти пользователя"),
    ),
    SwitchTo(
        state=states.ORG.NEW_TICKET,
        id="new_ticket",
        text=Const("🎫 Добавить новый билет"),
    ),
    Checkbox(
        Const("🔴 Выключить голосование"),
        Const("🟢 Включить голосование"),
        id=ID_VOTING_ENABLED_CHECKBOX,
        on_state_changed=switch_voting,
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.ORG.MAIN,
    getter=org_menu_getter,
)
