from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input.text import ManagedTextInputAdapter, TextInput
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
from sqlalchemy import and_

from src.bot.dialogs import states
from src.bot.dialogs.schedule.common import (
    EventsList,
    SchedulePaginator,
    get_schedule,
    on_wrong_event_id,
)
from src.bot.structures import UserRole
from src.bot.ui import strings
from src.config import conf
from src.db import Database
from src.db.models import Event, Subscription, User

EVENT_ID_INPUT = "subscribe_event_id_input"
ID_SUBSCRIPTIONS_SCROLL = "subscriptions_scroll"
SUBSCRIPTIONS_PER_PAGE = conf.bot.participants_per_page

# fmt: off
SubscriptionsList = Jinja(  # noqa: E501
    "{% if subscriptions|length == 0 %}"
        "У вас нет подписок 🔕\n"
    "{% else %}"
        "{% for subscription in subscriptions %}"
            "<b>{{ subscription.event.id }}.</b> {{ subscription.event.joined_title }}"
            "{% if subscription.event.real_position - current_event_position > 0 %}"
                "{% set counter = subscription.event.real_position - current_event_position %}"  # noqa: E501
                " <b>[осталось "
                "{% if (counter % 10 == 1) and (counter % 100 != 11) %}"
                    "{{ counter }} выступление"
                "{% elif (2 <= counter % 10 <= 4) and (counter % 100 < 10 or counter % 100 >= 20) %}"  # noqa: E501
                    "{{ counter }} выступления"
                "{% else %}"
                    "{{ counter }} выступлений"
                "{% endif %}"
                "{% if counter > subscription.counter %}"
                    ", начнём оповещать за "
                    "{% if (subscription.counter % 10 == 1) and (subscription.counter % 100 != 11) %}"  # noqa: E501
                        "{{ subscription.counter }} выступление]</b>"
                    "{% elif (2 <= subscription.counter % 10 <= 4) and (subscription.counter % 100 < 10 or subscription.counter % 100 >= 20) %}"  # noqa: E501
                        "{{ subscription.counter }} выступления]</b>"
                    "{% else %}"
                        "{{ subscription.counter }} выступлений]</b>"
                    "{% endif %}"
                "{% else %}"
                    "]</b>"
                "{% endif %}"
            "{% endif %}"
            "\n\n"
        "{% endfor %}"
    "{% endif %}"
)
# fmt: on


async def get_subscriptions(
    dialog_manager: DialogManager, db: Database, user: User, **kwargs
):
    pages = await db.subscription.get_number_of_pages(
        SUBSCRIPTIONS_PER_PAGE, Subscription.user_id == user.id
    )
    if pages == 0:
        pages = 1
    current_page = await dialog_manager.find(ID_SUBSCRIPTIONS_SCROLL).get_page()
    subscriptions = await db.subscription.get_page(
        current_page,
        SUBSCRIPTIONS_PER_PAGE,
        Subscription.user_id == user.id,
        order_by=Subscription.event_id,
    )
    current_event = await db.event.get_current()
    return {
        "pages": pages,
        "subscriptions": subscriptions,
        "receive_all_announcements": user.receive_all_announcements,
        "current_event_position": current_event.real_position if current_event else 0,
    }


async def proceed_input(
    message: Message,
    widget: ManagedTextInputAdapter,
    dialog_manager: DialogManager,
    data: str,
):
    db: Database = dialog_manager.middleware_data["db"]
    user: User = dialog_manager.middleware_data["user"]

    if not data.isnumeric():
        dialog_manager.dialog_data["search_query"] = data
        return

    event = await db.event.get_by_where(
        and_(
            Event.id == int(data),
            Event.hidden.isnot(True if user.role == UserRole.VISITOR else None),
        )
    )

    if not event:
        await message.reply("⚠️ Выступление не найдено!")
        return
    if event.hidden:
        await message.reply("⚠️ Нельзя подписаться на скрытое выступление!")
        return
    subscription = await db.subscription.get_by_where(
        and_(
            Subscription.event_id == event.id,
            Subscription.user_id == message.from_user.id,
        )
    )
    if subscription:
        await message.reply("⚠️ Вы уже подписаны на это выступление!")
        return
    else:
        dialog_manager.dialog_data["selected_event_title"] = event.joined_title
        await dialog_manager.switch_to(states.SCHEDULE.ASK_SUBSCRIPTION_COUNTER)


async def setup_subscription(
    message: Message,
    widget: ManagedTextInputAdapter,
    dialog_manager: DialogManager,
    data: int,
):
    db: Database = dialog_manager.middleware_data["db"]
    event_count = await db.event.get_count()
    if (data > event_count) or (data < 0):
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

    await dialog_manager.switch_to(states.SCHEDULE.SUBSCRIPTIONS_MANAGEMENT)


async def toggle_all_notifications(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    user: User = manager.middleware_data["user"]
    db: Database = manager.middleware_data["db"]
    user.receive_all_announcements = not user.receive_all_announcements
    await db.session.commit()


async def remove_subscription(
    message: Message,
    widget: ManagedTextInputAdapter,
    dialog_manager: DialogManager,
    data: int,
):
    db: Database = dialog_manager.middleware_data["db"]

    subscription = await db.subscription.get_by_where(Subscription.event_id == data)
    if subscription:
        await db.session.delete(subscription)
        await db.session.commit()
        await message.reply("🗑️ Подписка удалена!")
    else:
        await message.reply("⚠️ Подписка не найдена!")
        return


setup_subscription_window = Window(
    Format(
        "🔢 За сколько выступлений до начала "
        "<b>{dialog_data[selected_event_title]}</b> начать оповещать Вас?"
    ),
    TextInput(id="counter_input", type_factory=int, on_success=setup_subscription),
    SwitchTo(
        text=Const(strings.buttons.back),
        state=states.SCHEDULE.EVENT_CHOOSER,
        id="back",
    ),
    state=states.SCHEDULE.ASK_SUBSCRIPTION_COUNTER,
)

event_selection_window = Window(
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
        state=states.SCHEDULE.SUBSCRIPTIONS_MANAGEMENT,
        id="back",
    ),
    getter=get_schedule,
    state=states.SCHEDULE.EVENT_CHOOSER,
)

subscriptions_window = Window(
    Const("<b>🔔 Ваши подписки</b>\n"),
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
        state=states.SCHEDULE.EVENT_CHOOSER,
        id="subscribe",
    ),
    Button(
        text=Case(
            texts={
                True: Const("🔕 Получать только свои уведомления"),
                False: Const("🔔 Получать уведомления о всех выступлениях"),
            },
            selector=F["receive_all_announcements"],
        ),
        on_click=toggle_all_notifications,
        id="receive_all_announcements",
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
    SwitchTo(
        text=Const(strings.buttons.back),
        state=states.SCHEDULE.MAIN,
        id="back",
    ),
    getter=get_subscriptions,
    state=states.SCHEDULE.SUBSCRIPTIONS_MANAGEMENT,
)
