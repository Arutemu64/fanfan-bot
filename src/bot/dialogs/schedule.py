import asyncio
import math
import time

from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.input.text import ManagedTextInputAdapter
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    FirstPage,
    Group,
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
from src.bot.services import notifier
from src.bot.structures.role import Role
from src.bot.ui import strings
from src.cache import Cache
from src.config import conf
from src.db import Database
from src.db.models import Event, Subscription, User

per_page = conf.bot.events_per_page

ID_SCHEDULE_SCROLL = "schedule_scroll"


async def get_schedule(dialog_manager: DialogManager, db: Database, **kwargs):
    pages = math.ceil((await db.event.get_count() / per_page))
    if dialog_manager.start_data.get("current_page"):
        current_page = dialog_manager.start_data.pop("current_page")
    else:
        current_page = await dialog_manager.find(ID_SCHEDULE_SCROLL).get_page()
    events = await db.event.get_range(
        (current_page * per_page), (current_page * per_page) + per_page, Event.id
    )
    subscriptions = []
    for event in events:
        subscription = await db.session.scalar(
            event.subscriptions.select().where(
                User.id == dialog_manager.event.from_user.id
            )
        )
        subscriptions.append(subscription)
    user: User = dialog_manager.middleware_data.get("user")
    if user.role in [Role.HELPER, Role.ORG]:
        is_helper = True
    else:
        is_helper = False
    return {
        "pages": pages,
        "current_page": current_page + 1,
        "events": events,
        "is_helper": is_helper,
        "subscriptions": subscriptions,
    }


async def set_current_schedule_page(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    db: Database = manager.middleware_data["db"]
    current_event = await db.event.get_by_where(Event.current == True)  # noqa
    if current_event:
        current_event_id = current_event.id
    else:
        current_event_id = 1
    current_page = math.floor((current_event_id - 1) / per_page)
    await manager.find(ID_SCHEDULE_SCROLL).set_page(current_page)


async def toggle_helper_tools(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    toggle = manager.dialog_data.get("helper_tools_toggle")
    if toggle is True:
        manager.dialog_data["helper_tools_toggle"] = False
    else:
        manager.dialog_data["helper_tools_toggle"] = True


async def set_next_event(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    cache: Cache = manager.middleware_data["cache"]
    global_timestamp = float(await cache.get("announcement_timestamp"))
    if global_timestamp:
        timestamp = time.time()
        if (timestamp - global_timestamp) < conf.bot.announcement_timeout:
            await callback.answer(strings.errors.announce_too_fast, show_alert=True)
            return
    await cache.set("announcement_timestamp", time.time())

    db: Database = manager.middleware_data["db"]
    current_event = await db.event.get_by_where(Event.current == True)  # noqa
    if current_event:
        next_event = await db.event.get(current_event.id + 1)
        if not next_event:
            await callback.answer("Выступления закончились!", show_alert=True)
            return
        current_event.current = None
        await db.session.flush([current_event])
    else:
        next_event = await db.event.get(1)

    next_event.current = True
    await db.session.flush([next_event])
    await db.session.commit()

    await asyncio.create_task(
        notifier.send_subscription_notifications(bot=callback.bot, db=db)
    )

    current_page = math.floor((next_event.id - 1) / per_page)
    await manager.find(ID_SCHEDULE_SCROLL).set_page(current_page)


async def set_manual_event(
    message: Message,
    widget: ManagedTextInputAdapter,
    dialog_manager: DialogManager,
    data: int,
):
    db: Database = dialog_manager.middleware_data["db"]

    current_event = await db.event.get_by_where(Event.current == True)
    if current_event:
        current_event.current = None
        await db.session.flush([current_event])

    current_event = await db.event.get(data)
    if not current_event:
        await message.reply("Выступление не найдено!")
        return
    current_event.current = True
    await db.session.flush([current_event])
    await db.session.commit()

    await asyncio.create_task(
        notifier.send_subscription_notifications(bot=message.bot, db=db)
    )

    current_page = math.floor((current_event.id - 1) / per_page)
    await dialog_manager.find(ID_SCHEDULE_SCROLL).set_page(current_page)
    await dialog_manager.switch_to(states.SCHEDULE.MAIN)


async def swap_events(
    message: Message,
    widget: ManagedTextInputAdapter,
    dialog_manager: DialogManager,
    data: str,
):
    args = data.split()
    if len(args) != 2:
        await message.reply("Вы должны указать две позиции!")
        return
    if not (args[0].isnumeric() and args[1].isnumeric()):
        await message.reply("Неверно указаны позиции выступлений!")
        return

    db: Database = dialog_manager.middleware_data["db"]

    event1, event2 = await db.event.get(int(args[0])), await db.event.get(int(args[1]))
    if not event1 or not event2:
        await message.reply("Выступления не найдены!")
        return
    event1_id, event2_id = event1.id, event2.id

    event1.id, event2.id = event1.id * 10000, event2.id * 10000
    await db.session.flush([event1, event2])
    event1.id, event2.id = event2_id, event1_id
    await db.session.flush([event1, event2])
    await db.session.commit()

    await asyncio.create_task(
        notifier.send_subscription_notifications(bot=message.bot, db=db)
    )

    current_event = await db.event.get_by_where(Event.current == True)  # noqa
    if current_event:
        current_event_id = current_event.id
    else:
        current_event_id = 1
    current_page = math.floor((current_event_id - 1) / per_page)
    await dialog_manager.find(ID_SCHEDULE_SCROLL).set_page(current_page)
    await dialog_manager.switch_to(states.SCHEDULE.MAIN)


async def check_subscription(
    message: Message,
    widget: ManagedTextInputAdapter,
    dialog_manager: DialogManager,
    data: int,
):
    db: Database = dialog_manager.middleware_data["db"]
    subscription = await db.subscription.get_by_where(
        and_(
            Subscription.event_id == data, Subscription.user_id == message.from_user.id
        )
    )
    if subscription:
        await db.session.delete(subscription)
        await db.session.commit()
        await message.reply("Подписка удалена!")
        await dialog_manager.switch_to(states.SCHEDULE.MAIN)
    else:
        await dialog_manager.switch_to(states.SCHEDULE.ASK_SUBSCRIPTION_COUNTER)


async def setup_subscription(
    message: Message,
    widget: ManagedTextInputAdapter,
    dialog_manager: DialogManager,
    data: int,
):
    if data < 1:
        await message.reply("Некорректное значение")
        return
    event_id = dialog_manager.find("event_id_input").get_value()
    counter = data

    db: Database = dialog_manager.middleware_data["db"]
    subscription = await db.subscription.new(
        event_id=event_id, user_id=message.from_user.id, counter=counter
    )
    db.session.add(subscription)
    await db.session.commit()
    await message.reply("✅ Подписка оформлена успешно!")
    await dialog_manager.switch_to(states.SCHEDULE.MAIN)


# fmt: off
events_html = Jinja(
    "{% for event in events %}"
        "{% if event.participant %}"
            "{% if loop.previtem %}"
                "{% if loop.previtem.participant %}"
                    "{% if event.participant.nomination.id != loop.previtem.participant.nomination.id %}"
                        "<b>➡️ {{event.participant.nomination.title}}</b>\n"
                    "{% endif %}"
                "{% else %}"
                    "<b>➡️ {{event.participant.nomination.title}}</b>\n"
                "{% endif %}"
            "{% else %}"
                "<b>➡️ {{event.participant.nomination.title}}</b>\n"
            "{% endif %}"
        "{% endif %}"
        "{% if event.current %}"
            "<b>"
        "{% endif %}"
        "{% if event.participant %}"
            "<b>{{event.id}}.</b> {{event.participant.title}}"
        "{% elif event.title %}"
            "<i>{{event.id}}. {{event.title}}</i>"
        "{% endif %}"
        "{% if event.current %}"
            "</b> 👈"
        "{% endif %}"
        "{% if subscriptions[loop.index-1] %}"
            " 🔔"
        "{% endif %}"
        "\n\n"
    "{% endfor %}")
# fmt: on


SchedulePaginator = Row(
    FirstPage(scroll=ID_SCHEDULE_SCROLL, text=Const("⏪")),
    PrevPage(scroll=ID_SCHEDULE_SCROLL, text=Const("◀️")),
    Button(
        text=Format(text="{current_page}/{pages} 🔄️"),
        id="update",
        on_click=set_current_schedule_page,
    ),
    NextPage(scroll=ID_SCHEDULE_SCROLL, text=Const("▶️")),
    LastPage(scroll=ID_SCHEDULE_SCROLL, text=Const("⏭️")),
)

schedule = Window(
    Const("<b>📅 Расписание</b>\n"),
    events_html,
    Const(
        "Чтобы подписаться на выступление (или отписаться), отправьте его номер сообщением 👇"
    ),
    TextInput(
        id="event_id_input",
        type_factory=int,
        on_success=check_subscription,
    ),
    StubScroll(ID_SCHEDULE_SCROLL, pages="pages"),
    Button(
        text=Case(
            texts={
                True: Const("🧰 ⬇️ Инструменты волонтёра"),
                False: Const("🧰 ⬆️ Инструменты волонтёра"),
                None: Const("🧰 ⬆️ Инструменты волонтёра"),
            },
            selector=F["dialog_data"]["helper_tools_toggle"],
        ),
        id="toggle_helper_tools",
        on_click=toggle_helper_tools,
        when="is_helper",
    ),
    Group(
        Row(
            Button(
                text=Const("⏭️ Следующее"),
                id="next_event",
                on_click=set_next_event,
            ),
            SwitchTo(
                text=Const("👆 Указать вручную"),
                id="manual_event",
                state=states.SCHEDULE.ASK_MANUAL_EVENT,
            ),
        ),
        SwitchTo(
            text=Const("🔃 Поменять местами"),
            id="swap_events",
            state=states.SCHEDULE.SWAP_EVENTS,
        ),
        when=F["dialog_data"]["helper_tools_toggle"],
    ),
    SchedulePaginator,
    Cancel(text=Const(strings.buttons.back)),
    state=states.SCHEDULE.MAIN,
    getter=get_schedule,
)


set_manual_event_window = Window(
    Const("<b>Укажите номер текущего выступления:</b>\n"),
    TextInput(
        id="manual_event_input",
        type_factory=int,
        on_success=set_manual_event,
    ),
    events_html,
    SchedulePaginator,
    SwitchTo(state=states.SCHEDULE.MAIN, text=Const(strings.buttons.back), id="back"),
    state=states.SCHEDULE.ASK_MANUAL_EVENT,
    getter=get_schedule,
)


swap_events_window = Window(
    Const("<b>Укажите номера двух выступлений, которые нужно поменять местами:</b>\n"),
    TextInput(
        id="manual_event_input",
        type_factory=str,
        on_success=swap_events,
    ),
    events_html,
    SchedulePaginator,
    SwitchTo(state=states.SCHEDULE.MAIN, text=Const(strings.buttons.back), id="back"),
    state=states.SCHEDULE.SWAP_EVENTS,
    getter=get_schedule,
)


setup_subscription_window = Window(
    Const("За сколько выступлений до начать оповещать вас?"),
    TextInput(id="counter_input", type_factory=int, on_success=setup_subscription),
    state=states.SCHEDULE.ASK_SUBSCRIPTION_COUNTER,
)

dialog = Dialog(
    schedule, set_manual_event_window, swap_events_window, setup_subscription_window
)
