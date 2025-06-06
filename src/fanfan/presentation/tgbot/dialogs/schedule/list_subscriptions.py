from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    CurrentPage,
    FirstPage,
    LastPage,
    NextPage,
    PrevPage,
    Row,
    StubScroll,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Case, Const, Format, Jinja
from dishka import AsyncContainer

from fanfan.application.schedule.read_event_by_public_id import (
    ReadScheduleEventByPublicId,
)
from fanfan.application.schedule.subscriptions.read_subscriptions_page import (
    GetSubscriptionsPage,
)
from fanfan.application.users.update_user_settings import (
    UpdateUserSettings,
)
from fanfan.core.dto.page import Pagination
from fanfan.core.models.user import UserData
from fanfan.core.vo.schedule_event import ScheduleEventPublicId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.schedule.common import (
    current_event_getter,
)
from fanfan.presentation.tgbot.dialogs.schedule.view_event import show_event_details
from fanfan.presentation.tgbot.static import strings
from fanfan.presentation.tgbot.templates import subscriptions_list

ID_SUBSCRIPTIONS_SCROLL = "subscriptions_scroll"
ID_RECEIVE_ALL_ANNOUNCEMENTS_CHECKBOX = "receive_all_announcements_checkbox"


async def subscriptions_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    user: UserData,
    **kwargs,
):
    get_subscriptions_page: GetSubscriptionsPage = await container.get(
        GetSubscriptionsPage
    )

    page = await get_subscriptions_page(
        pagination=Pagination(
            limit=user.settings.items_per_page,
            offset=await dialog_manager.find(ID_SUBSCRIPTIONS_SCROLL).get_page()
            * user.settings.items_per_page,
        )
    )
    pages = page.total // user.settings.items_per_page + bool(
        page.total % user.settings.items_per_page
    )
    return {
        "subscriptions": page.items,
        "pages": pages or 1,
        "receive_all_announcements": user.settings.receive_all_announcements,
    }


async def subscriptions_text_input_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    container: AsyncContainer = dialog_manager.middleware_data["container"]
    if "/" in data and data.replace("/", "").isnumeric():
        public_event_id = ScheduleEventPublicId(int(data.replace("/", "")))
        get_event_id_by_public_id = await container.get(ReadScheduleEventByPublicId)
        event = await get_event_id_by_public_id(public_event_id)
        await show_event_details(dialog_manager, event.id)


async def toggle_all_notifications_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    user: UserData = manager.middleware_data["user"]
    container: AsyncContainer = manager.middleware_data["container"]
    update_user_settings: UpdateUserSettings = await container.get(UpdateUserSettings)

    await update_user_settings.toggle_receive_all_announcements(
        not user.settings.receive_all_announcements
    )
    await manager.bg().update(data={})


subscriptions_main_window = Window(
    Title(Const(strings.titles.notifications)),
    Jinja(subscriptions_list),
    Const(
        "➕ <i>Чтобы подписаться, нажми на номер выступления в расписании</i>",
        when=~F["subscriptions"],
    ),
    TextInput(
        id="subscriptions_text_input",
        type_factory=str,
        on_success=subscriptions_text_input_handler,
    ),
    Button(
        Case(
            {
                True: Const("📣 Получать общие уведомления: ✅"),
                False: Const("📣 Получать общие уведомления: ❌"),
            },
            selector="receive_all_announcements",
        ),
        id=ID_RECEIVE_ALL_ANNOUNCEMENTS_CHECKBOX,
        on_click=toggle_all_notifications_handler,
    ),
    StubScroll(ID_SUBSCRIPTIONS_SCROLL, pages="pages"),
    Row(
        FirstPage(scroll=ID_SUBSCRIPTIONS_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_SUBSCRIPTIONS_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_SUBSCRIPTIONS_SCROLL,
            text=Format(text="{current_page1}/{pages}"),
        ),
        NextPage(scroll=ID_SUBSCRIPTIONS_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_SUBSCRIPTIONS_SCROLL, text=Const("⏭️")),
    ),
    SwitchTo(
        text=Const(strings.buttons.back),
        id="back",
        state=states.Schedule.MAIN,
    ),
    getter=[subscriptions_getter, current_event_getter],
    state=states.Schedule.SUBSCRIPTIONS,
)
