from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Counter, ManagedCounter, SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.users.update_user_settings import UpdateUserSettings
from fanfan.core.dto.user import FullUserDTO
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.utils import (
    get_current_user,
    refresh_current_user,
)
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings

ID_ITEMS_PER_PAGE_INPUT = "items_per_page_input"


async def user_settings_getter(
    dialog_manager: DialogManager,
    current_user: FullUserDTO,
    **kwargs,
):
    return {
        "items_per_page": current_user.settings.items_per_page,
    }


async def update_counter_value_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    current_user: FullUserDTO = get_current_user(manager)
    await manager.find(ID_ITEMS_PER_PAGE_INPUT).set_value(
        current_user.settings.items_per_page
    )


@inject
async def items_per_page_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    update_user_settings: FromDishka[UpdateUserSettings],
) -> None:
    counter: ManagedCounter = manager.find(ID_ITEMS_PER_PAGE_INPUT)
    await update_user_settings.set_items_per_page(int(counter.get_value()))
    await refresh_current_user(manager)
    await callback.answer("✅ Успешно!")
    await manager.switch_to(state=states.Settings.USER_SETTINGS)


user_settings_window = Window(
    Title(Const(strings.titles.user_settings)),
    Const(
        "<b>📄 Элементов на странице</b> - сколько "
        "элементов будет отображаться в различных списках бота "
        "(расписание, голосование и т. д.)."
    ),
    SwitchTo(
        text=Jinja(
            "📄 Элементов на странице: [{{ items_per_page }}]",
        ),
        id="set_items_per_page_button",
        on_click=update_counter_value_handler,
        state=states.Settings.SET_ITEMS_PER_PAGE,
    ),
    SwitchTo(Const(strings.buttons.back), state=states.Settings.MAIN, id="back"),
    state=states.Settings.USER_SETTINGS,
    getter=user_settings_getter,
)


items_per_page_window = Window(
    Const(
        "📄 Укажите желаемое число элементов на странице <i>(от 1 до 10)</i>",
    ),
    Counter(
        id=ID_ITEMS_PER_PAGE_INPUT,
        plus=Const("➕"),
        minus=Const("➖"),
        min_value=1,
        max_value=10,
    ),
    Button(
        text=Const("💾 Сохранить"),
        id="save_items_per_page",
        on_click=items_per_page_handler,
    ),
    SwitchTo(
        text=Const(strings.buttons.back),
        id="back",
        state=states.Settings.USER_SETTINGS,
    ),
    state=states.Settings.SET_ITEMS_PER_PAGE,
)
