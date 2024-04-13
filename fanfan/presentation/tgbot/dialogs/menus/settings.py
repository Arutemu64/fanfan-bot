from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Counter, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, List

from fanfan.application.dto.user import (
    FullUserDTO,
    UpdateUserSettingsDTO,
)
from fanfan.application.exceptions import ServiceError
from fanfan.application.holder import AppHolder
from fanfan.presentation.tgbot.dialogs import states
from fanfan.presentation.tgbot.dialogs.widgets import Title
from fanfan.presentation.tgbot.ui import strings

ID_ITEMS_PER_PAGE_INPUT = "items_per_page_input"


async def user_info_getter(dialog_manager: DialogManager, user: FullUserDTO, **kwargs):
    return {
        "user": user,
        "user_info_list": [
            ("Никнейм:", user.username),
            ("ID:", user.id),
            (
                "Билет:",
                user.ticket.id if user.ticket else "не привязан",
            ),
            ("Роль:", user.role.label),
        ],
    }


async def update_counter_value(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    user: FullUserDTO = manager.middleware_data["user"]
    await manager.find(ID_ITEMS_PER_PAGE_INPUT).set_value(user.settings.items_per_page)


async def items_per_page_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    app: AppHolder = manager.middleware_data["app"]
    user: FullUserDTO = manager.middleware_data["user"]
    try:
        await app.users.update_user_settings(
            UpdateUserSettingsDTO(
                user_id=manager.event.from_user.id,
                items_per_page=manager.find(ID_ITEMS_PER_PAGE_INPUT).get_value(),
            ),
        )
        manager.middleware_data["user"] = await app.users.get_user_by_id(user.id)
    except ServiceError as e:
        await callback.answer(e.message)
        return
    await callback.answer("✅ Успешно!")
    await manager.switch_to(state=states.SETTINGS.MAIN)


items_per_page_window = Window(
    Const(
        "🔢 <b>Укажите, сколько выступлений/участников выводить "
        "на одной странице</b> <i>(от 3 до 10)</i>",
    ),
    Counter(
        id=ID_ITEMS_PER_PAGE_INPUT,
        plus=Const("➕"),
        minus=Const("➖"),
        min_value=3,
        max_value=10,
    ),
    Button(
        text=Const("💾 Сохранить"),
        id="save_items_per_page",
        on_click=items_per_page_handler,
    ),
    state=states.SETTINGS.SET_ITEMS_PER_PAGE,
)

settings_main_window = Window(
    Title(Const(strings.titles.settings)),
    List(Format("<b>{item[0]}</b> {item[1]}"), items="user_info_list"),
    SwitchTo(
        text=Format("🔢 Элементов на страницу: {user.settings.items_per_page}"),
        id="set_items_per_page_button",
        on_click=update_counter_value,
        state=states.SETTINGS.SET_ITEMS_PER_PAGE,
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.SETTINGS.MAIN,
    getter=user_info_getter,
)

dialog = Dialog(settings_main_window, items_per_page_window)
