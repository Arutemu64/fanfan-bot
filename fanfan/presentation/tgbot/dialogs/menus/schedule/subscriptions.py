from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input.text import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
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

from fanfan.application.dto.subscription import CreateSubscriptionDTO
from fanfan.application.dto.user import FullUserDTO, UpdateUserDTO
from fanfan.application.exceptions import ServiceError
from fanfan.application.exceptions.event import (
    EventNotFound,
    NoCurrentEvent,
    SkippedEventNotAllowed,
)
from fanfan.application.exceptions.subscriptions import (
    SubscriptionAlreadyExist,
    SubscriptionNotFound,
)
from fanfan.application.holder import AppHolder
from fanfan.presentation.tgbot.dialogs import (
    states,
)
from fanfan.presentation.tgbot.dialogs.menus.schedule.common import (
    ScheduleWindow,
    set_search_query_handler,
)
from fanfan.presentation.tgbot.dialogs.widgets import Title
from fanfan.presentation.tgbot.static.templates import subscriptions_list
from fanfan.presentation.tgbot.ui import strings

ID_SUBSCRIPTIONS_SCROLL = "subscriptions_scroll"
ID_EVENT_INPUT = "event_input"
ID_RECEIVE_ALL_ANNOUNCEMENTS_CHECKBOX = "receive_all_announcements_checkbox"

DATA_SELECTED_EVENT_TITLE = "selected_event_title"
DATA_SELECTED_EVENT_ID = "data_selected_event_id"


async def subscriptions_getter(
    dialog_manager: DialogManager,
    user: FullUserDTO,
    app: AppHolder,
    **kwargs,
):
    page = await app.subscriptions.get_subscriptions_page(
        page_number=await dialog_manager.find(ID_SUBSCRIPTIONS_SCROLL).get_page(),
        subscriptions_per_page=user.items_per_page,
        user_id=user.id,
    )
    try:
        current_event = await app.schedule.get_current_event()
    except NoCurrentEvent:
        current_event = None
    return {
        "receive_all_announcements": user.receive_all_announcements,
        "pages": page.total_pages,
        "subscriptions": page.items,
        "current_event": current_event,
    }


async def create_subscription_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
):
    app: AppHolder = dialog_manager.middleware_data["app"]
    try:
        await app.subscriptions.get_subscription_by_event(
            user_id=dialog_manager.event.from_user.id,
            event_id=data,
        )
    except SubscriptionNotFound:
        try:
            event = await app.schedule.get_event(data)
        except EventNotFound as e:
            await message.reply(e.message)
            return
        if event.skip:
            await message.reply(SkippedEventNotAllowed.message)
            return
        dialog_manager.dialog_data[DATA_SELECTED_EVENT_ID] = data
        dialog_manager.dialog_data[DATA_SELECTED_EVENT_TITLE] = event.title
        await dialog_manager.switch_to(states.SUBSCRIPTIONS.SET_COUNTER)
        return
    await message.reply(SubscriptionAlreadyExist.message)


async def set_counter_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
):
    app: AppHolder = dialog_manager.middleware_data["app"]
    try:
        subscription = await app.subscriptions.create_subscription(
            CreateSubscriptionDTO(
                user_id=dialog_manager.event.from_user.id,
                event_id=dialog_manager.dialog_data[DATA_SELECTED_EVENT_ID],
                counter=data,
            ),
        )
    except ServiceError as e:
        await message.reply(e.message)
        return
    await message.reply(
        f"✅ Подписка на выступление "
        f"<b>{subscription.event.title}</b>"
        f" успешно оформлена!",
    )
    await dialog_manager.switch_to(states.SUBSCRIPTIONS.MAIN)


async def remove_subscription_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
):
    app: AppHolder = dialog_manager.middleware_data["app"]
    try:
        await app.subscriptions.delete_subscription_by_event(
            user_id=dialog_manager.event.from_user.id,
            event_id=data,
        )
    except ServiceError as e:
        await message.reply(e.message)
        return

    await message.reply("🗑️ Подписка удалена!")


async def toggle_all_notifications_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    user: FullUserDTO = manager.middleware_data["user"]
    app: AppHolder = manager.middleware_data["app"]
    try:
        manager.middleware_data["user"] = await app.users.update_user(
            UpdateUserDTO(
                id=user.id,
                receive_all_announcements=not user.receive_all_announcements,
            ),
        )
    except ServiceError as e:
        await callback.answer(e.message)


set_counter_window = Window(
    Format(
        """🔢 За сколько выступлений до начала """
        """<b>{dialog_data[selected_event_title]}</b> начать оповещать Вас?""",
    ),
    TextInput(
        id="counter_input",
        type_factory=int,
        on_success=set_counter_handler,
    ),
    SwitchTo(
        text=Const(strings.buttons.back),
        id="back",
        state=states.SUBSCRIPTIONS.SELECT_EVENT,
    ),
    state=states.SUBSCRIPTIONS.SET_COUNTER,
)

select_event_window = ScheduleWindow(
    state=states.SUBSCRIPTIONS.SELECT_EVENT,
    header=Title(
        Const("➕ Пришлите номер выступления, на которое хотите подписаться:"),
        upper=False,
    ),
    after_paginator=SwitchTo(
        text=Const(strings.buttons.back),
        state=states.SUBSCRIPTIONS.MAIN,
        id="back",
    ),
    text_input=TextInput(
        id=ID_EVENT_INPUT,
        type_factory=int,
        on_success=create_subscription_handler,
        on_error=set_search_query_handler,
    ),
)

subscriptions_main_window = Window(
    Title(Const(strings.titles.notifications)),
    Jinja(subscriptions_list),
    Const(
        "🗑️ <i>Чтобы отписаться, пришлите номер выступления</i>",
        when=F["subscriptions"],
    ),
    TextInput(
        id="REMOVE_SUBSCRIPTION_INPUT",
        type_factory=int,
        on_success=remove_subscription_handler,
    ),
    SwitchTo(
        text=Const("➕ Подписаться на выступление"),
        state=states.SUBSCRIPTIONS.SELECT_EVENT,
        id="subscribe",
    ),
    Button(
        Case(
            {
                True: Const("🔕 Получать только свои уведомления"),
                False: Const("🔔 Получать все уведомления"),
            },
            selector=F["receive_all_announcements"],
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
        when=F["pages"] > 1,
    ),
    Cancel(Const(strings.buttons.back)),
    getter=subscriptions_getter,
    state=states.SUBSCRIPTIONS.MAIN,
)

dialog = Dialog(subscriptions_main_window, select_event_window, set_counter_window)
