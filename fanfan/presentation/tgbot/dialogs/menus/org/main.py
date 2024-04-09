import operator

import jwt
from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    Column,
    ManagedRadio,
    Radio,
    Start,
    SwitchTo,
    Url,
)
from aiogram_dialog.widgets.text import Case, Const, Format

from fanfan.application.exceptions import ServiceError
from fanfan.application.holder import AppHolder
from fanfan.common.enums import UserRole
from fanfan.config import get_config
from fanfan.presentation.tgbot.dialogs import states
from fanfan.presentation.tgbot.dialogs.getters import get_roles
from fanfan.presentation.tgbot.dialogs.widgets import Title
from fanfan.presentation.tgbot.ui import strings

ID_TICKET_ROLE_PICKER = "ticket_role_picker"
ID_TOGGLE_VOTING_BUTTON = "toggle_voting_button"

DATA_VOTING_ENABLED = "voting_enabled"


async def org_menu_getter(dialog_manager: DialogManager, app: AppHolder, **kwargs):
    settings = await app.settings.get_settings()
    dialog_manager.dialog_data[DATA_VOTING_ENABLED] = settings.voting_enabled
    jwt_token = jwt.encode(
        payload={"user_id": dialog_manager.event.from_user.id},
        key=get_config().web.secret_key.get_secret_value(),
    )
    return {
        "voting_enabled": settings.voting_enabled,
        "web_panel_login_link": f"{get_config().web.build_admin_auth_url()}"
        f"?token={jwt_token}",
    }


async def toggle_voting_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    app: AppHolder = manager.middleware_data["app"]
    await app.settings.switch_voting(not manager.dialog_data[DATA_VOTING_ENABLED])


async def add_new_ticket_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    app: AppHolder = dialog_manager.middleware_data["app"]
    role_picker: ManagedRadio[UserRole] = dialog_manager.find(ID_TICKET_ROLE_PICKER)

    try:
        ticket = await app.tickets.create_ticket(
            ticket_id=data,
            role=role_picker.get_checked(),
        )
    except ServiceError as e:
        await message.answer(e.message)
        return

    await message.answer(
        f"""✅ Билет "{ticket.id}" с ролью {ticket.role} успешно добавлен!""",
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
            type_factory=UserRole,
        ),
    ),
    TextInput(id="ticket_id", type_factory=str, on_success=add_new_ticket_handler),
    SwitchTo(
        state=states.ORG.MAIN,
        id="org_main_window",
        text=Const(strings.buttons.back),
    ),
    getter=get_roles,
    state=states.ORG.ADD_NEW_TICKET,
)

org_main_window = Window(
    Title(Const(strings.titles.org_menu)),
    Url(
        text=Const("🌐 Перейти в панель организатора"),
        url=Format("{web_panel_login_link}"),
    ),
    Url(
        text=Const(strings.buttons.help_page),
        url=Const("https://fan-fan.notion.site/7234cca8ae1943b18a5bc4435342fffe"),
    ),
    Start(
        state=states.DELIVERIES.MAIN,
        id="new_notification",
        text=Const("✉️ Рассылки"),
    ),
    Start(
        state=states.USER_MANAGER.MANUAL_USER_SEARCH,
        id="user_search",
        text=Const("🔍 Найти пользователя"),
    ),
    SwitchTo(
        state=states.ORG.ADD_NEW_TICKET,
        id="new_ticket",
        text=Const("🎫 Добавить новый билет"),
    ),
    Button(
        Case(
            {
                True: Const("🔴 Выключить голосование"),
                False: Const("🟢 Включить голосование"),
            },
            selector=F["voting_enabled"],
        ),
        id=ID_TOGGLE_VOTING_BUTTON,
        on_click=toggle_voting_handler,
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.ORG.MAIN,
    getter=org_menu_getter,
)
