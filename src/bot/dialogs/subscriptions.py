from aiogram import F
from aiogram.types import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.dialog import ChatEvent, Dialog
from aiogram_dialog.widgets.input.text import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Cancel,
    Checkbox,
    CurrentPage,
    FirstPage,
    LastPage,
    ManagedCheckbox,
    NextPage,
    PrevPage,
    Row,
    StubScroll,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, Jinja

from src.bot import TEMPLATES_DIR
from src.bot.dialogs import states
from src.bot.dialogs.getters import schedule_list
from src.bot.dialogs.schedule.common import (
    ID_SCHEDULE_SCROLL,
    EventsList,
    SchedulePaginator,
    on_wrong_event_id,
)
from src.bot.dialogs.widgets import Title
from src.bot.ui import strings
from src.db import Database

EVENT_ID_INPUT = "subscribe_event_id_input"
ID_SUBSCRIPTIONS_SCROLL = "subscriptions_scroll"
ID_RECEIVE_ALL_ANNOUNCEMENTS_CHECKBOX = "receive_all_announcements_checkbox"

with open(TEMPLATES_DIR / "subscriptions.jinja2", "r", encoding="utf-8") as file:
    SubscriptionsList = Jinja(file.read())


async def subscriptions_getter(dialog_manager: DialogManager, db: Database, **kwargs):
    page = await db.subscription.paginate(
        page=await dialog_manager.find(ID_SUBSCRIPTIONS_SCROLL).get_page(),
        subscriptions_per_page=dialog_manager.dialog_data["events_per_page"],
        user_id=dialog_manager.event.from_user.id,
    )
    current_event = await db.event.get_current()
    return {
        "pages": page.total,
        "subscriptions": page.items,
        "current_event_position": current_event.real_position if current_event else 0,
    }


async def schedule_getter(dialog_manager: DialogManager, db: Database, **kwargs):
    page = await dialog_manager.find(ID_SCHEDULE_SCROLL).get_page()
    data = await schedule_list(
        db=db,
        events_per_page=dialog_manager.dialog_data["events_per_page"],
        page=page,
        user_id=dialog_manager.event.from_user.id,
        search_query=dialog_manager.dialog_data.get("search_query"),
    )
    data.update({"page": page + 1})
    return data


async def proceed_input(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    db: Database = dialog_manager.middleware_data["db"]

    if not data.isnumeric():
        dialog_manager.dialog_data["search_query"] = data
        return

    event = await db.event.get(int(data))

    if not event:
        await message.reply("⚠️ Выступление не найдено!")
        return
    if event.skip:
        await message.reply("⚠️ На это выступление нельзя подписаться!")
        return
    if await db.subscription.get_subscription_for_user(event.id, message.from_user.id):
        await message.reply("⚠️ Вы уже подписаны на это выступление!")
        return
    else:
        dialog_manager.dialog_data["selected_event_title"] = event.joined_title
        await dialog_manager.switch_to(states.SUBSCRIPTIONS.SET_SUBSCRIPTION_COUNTER)


async def setup_subscription(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
):
    db: Database = dialog_manager.middleware_data["db"]

    if not 0 < data < await db.event.get_count():
        await message.reply("⚠️ Некорректное значение")
        return

    event_id = int(dialog_manager.find(EVENT_ID_INPUT).get_value())
    counter = data

    subscription = await db.subscription.new(
        event_id=event_id, user_id=message.from_user.id, counter=counter
    )
    db.session.add(subscription)
    await db.session.commit()
    await db.session.refresh(subscription)
    await message.reply(
        f"✅ Подписка на выступление "
        f"<b>{subscription.event.joined_title}</b>"
        f" успешно оформлена!"
    )

    await dialog_manager.switch_to(states.SUBSCRIPTIONS.MAIN)


async def remove_subscription(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
):
    db: Database = dialog_manager.middleware_data["db"]

    if data.bit_length() > 32:
        await message.reply("⚠️ Некорректное значение!")
        return

    subscription = await db.subscription.get_subscription_for_user(
        event_id=data,
        user_id=dialog_manager.event.from_user.id,
    )
    if subscription:
        await db.subscription.delete(subscription.id)
        await db.session.commit()
        await message.reply("🗑️ Подписка удалена!")
    else:
        await message.reply("⚠️ Подписка не найдена!")
        return


async def toggle_all_notifications(
    event: ChatEvent, checkbox: ManagedCheckbox, manager: DialogManager
):
    db: Database = manager.middleware_data["db"]
    await db.user.set_receive_all_announcements(
        user_id=manager.event.from_user.id,
        value=checkbox.is_checked(),
    )
    await db.session.commit()


set_subscription_counter_window = Window(
    Format(
        "🔢 За сколько выступлений до начала "
        "<b>{dialog_data[selected_event_title]}</b> начать оповещать Вас?"
    ),
    TextInput(id="counter_input", type_factory=int, on_success=setup_subscription),
    SwitchTo(
        text=Const(strings.buttons.back),
        state=states.SUBSCRIPTIONS.EVENT_SELECTOR,
        id="back",
    ),
    state=states.SUBSCRIPTIONS.SET_SUBSCRIPTION_COUNTER,
)

event_selector_window = Window(
    Const("<b>➕ Пришлите номер выступления, на которое хотите подписаться:</b>\n"),
    EventsList,
    Const(
        "🔍 <i>Для поиска отправьте запрос сообщением</i>",
        when=~F["dialog_data"]["search_query"],
    ),
    SchedulePaginator,
    TextInput(
        id=EVENT_ID_INPUT,
        type_factory=str,
        on_success=proceed_input,
    ),
    SwitchTo(
        text=Const(strings.buttons.back),
        state=states.SUBSCRIPTIONS.MAIN,
        id="back",
    ),
    getter=schedule_getter,
    state=states.SUBSCRIPTIONS.EVENT_SELECTOR,
)

main_subscriptions_window = Window(
    Title(strings.titles.notifications),
    Const(""),
    SubscriptionsList,
    Const(
        "🗑️ <i>Чтобы отписаться, пришлите номер выступления</i>",
        when=F["subscriptions"],
    ),
    TextInput(
        id="REMOVE_SUBSCRIPTION_INPUT",
        type_factory=int,
        on_success=remove_subscription,
        on_error=on_wrong_event_id,
    ),
    SwitchTo(
        text=Const("➕ Подписаться на выступление"),
        state=states.SUBSCRIPTIONS.EVENT_SELECTOR,
        id="subscribe",
    ),
    Checkbox(
        Const("🔕 Получать только свои уведомления"),
        Const("🔔 Получать все уведомления"),
        id=ID_RECEIVE_ALL_ANNOUNCEMENTS_CHECKBOX,
        on_state_changed=toggle_all_notifications,
    ),
    StubScroll(ID_SUBSCRIPTIONS_SCROLL, pages="pages"),
    Row(
        FirstPage(scroll=ID_SUBSCRIPTIONS_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_SUBSCRIPTIONS_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_SUBSCRIPTIONS_SCROLL, text=Format(text="{current_page1}/{pages}")
        ),
        NextPage(scroll=ID_SUBSCRIPTIONS_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_SUBSCRIPTIONS_SCROLL, text=Const("⏭️")),
        when=F["pages"] != 1,
    ),
    Cancel(
        text=Const(strings.buttons.back),
    ),
    getter=subscriptions_getter,
    state=states.SUBSCRIPTIONS.MAIN,
)


async def on_start_subscriptions(start_data: dict, manager: DialogManager):
    db: Database = manager.middleware_data["db"]
    user = await db.user.get(manager.event.from_user.id)
    manager.dialog_data["events_per_page"] = user.items_per_page
    await manager.find(ID_RECEIVE_ALL_ANNOUNCEMENTS_CHECKBOX).set_checked(
        user.receive_all_announcements
    )
    pass


dialog = Dialog(
    main_subscriptions_window,
    event_selector_window,
    set_subscription_counter_window,
    on_start=on_start_subscriptions,
)
