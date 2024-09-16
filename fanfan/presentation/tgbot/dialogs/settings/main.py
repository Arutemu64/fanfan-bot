from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, Jinja

from fanfan.core.models.user import FullUserDTO
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.settings.common import ID_ITEMS_PER_PAGE_INPUT
from fanfan.presentation.tgbot.ui import strings


async def settings_user_info_getter(
    dialog_manager: DialogManager, user: FullUserDTO, **kwargs
):
    return {
        "username": user.username,
        "user_id": user.id,
        "ticket": user.ticket.id if user.ticket else "не привязан",
        "role": user.role.label,
        "items_per_page": user.settings.items_per_page,
    }


async def update_counter_value_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    user: FullUserDTO = manager.middleware_data["user"]
    await manager.find(ID_ITEMS_PER_PAGE_INPUT).set_value(user.settings.items_per_page)


settings_main_window = Window(
    Title(Const(strings.titles.settings)),
    Jinja("<b>Никнейм:</b> {{ username|e }}"),
    Format("<b>ID:</b> {user_id}"),
    Format("<b>Билет:</b> {ticket}"),
    Format("<b>Роль:</b> {role}"),
    SwitchTo(
        text=Format(
            "🔢 Количество элементов на странице: " "{items_per_page}",
        ),
        id="set_items_per_page_button",
        on_click=update_counter_value_handler,
        state=states.Settings.set_items_per_page,
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.Settings.main,
    getter=settings_user_info_getter,
)
