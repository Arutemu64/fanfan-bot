import asyncio

from aiogram import F
from aiogram.types import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.input.text import ManagedTextInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const
from sqlalchemy import text

from src.bot.dialogs import states
from src.bot.dialogs.schedule.common import (
    EventsList,
    SchedulePaginator,
    schedule_getter,
    set_schedule_page,
    set_search_query,
)
from src.bot.dialogs.schedule.tools import notifier
from src.bot.structures import UserRole
from src.bot.ui import strings
from src.db import Database
from src.db.models import User


async def proceed_input(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    db: Database = dialog_manager.middleware_data["db"]
    user: User = dialog_manager.middleware_data["current_user"]

    # Проверяем права
    if user.role < UserRole.HELPER:
        await message.reply(strings.errors.access_denied)
        return

    # Поиск
    if not data.isnumeric():
        await set_search_query(message, widget, dialog_manager, data)
        return

    # Получаем выступление, проверяем его существование
    event = await db.event.get(int(data))
    if not event:
        await message.reply("⚠️ Выступление не найдено!")
        return

    # Проверяем, что выступление не отмечено как текущее
    if event.current:
        await message.reply("⚠️ Текущее выступление нельзя отметить как скрытое")
        return

    # Получаем следующее выступление до скрытия
    current_event = await db.event.get_current()
    next_event_before = await db.event.get_next(current_event)

    # Переключаем статус "скрыто" для выступления
    await db.session.execute(text("SET CONSTRAINTS ALL DEFERRED"))
    event.skip = not event.skip
    await db.session.commit()
    await db.session.refresh(event, ["real_position"])

    # Выводим подтверждение
    if event.skip:
        await message.reply(f"🙈 Выступление <b>{event.title}</b> пропущено")
    if not event.skip:
        await message.reply(f"🙉 Выступление <b>{event.title}</b> возвращено")

    # Получаем следующее выступление после скрытия
    next_event_after = await db.event.get_next(current_event)

    # Если скрытие повлияло на следующее по расписанию
    # выступление - рассылаем глобальный анонс
    if next_event_after is not next_event_before:
        send_global_announcement = True
    else:
        send_global_announcement = False

    # Запускаем проверку подписок
    asyncio.create_task(
        notifier.proceed_subscriptions(
            arq=dialog_manager.middleware_data["arq"],
            send_global_announcement=send_global_announcement,
        )
    )

    # Отправляем пользователя на страницу со скрытым/открытым выступлением
    await set_schedule_page(dialog_manager, event)


toggle_event_skip_window = Window(
    Const("<b>🙈 Укажите номер выступления, которое Вы хотите скрыть/отобразить:</b>\n"),
    EventsList,
    Const(
        "🔍 <i>Для поиска отправьте запрос сообщением</i>",
        when=~F["dialog_data"]["search_query"],
    ),
    SchedulePaginator,
    TextInput(
        id="toggle_event_skip",
        type_factory=str,
        on_success=proceed_input,
    ),
    SwitchTo(state=states.SCHEDULE.MAIN, text=Const(strings.buttons.back), id="back"),
    state=states.SCHEDULE.TOGGLE_EVENT_SKIP,
    getter=schedule_getter,
)
