import asyncio
from contextlib import suppress

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from sqlalchemy import and_

from src.bot.dialogs.schedule.common import set_current_schedule_page
from src.bot.dialogs.schedule.tools.common import throttle_announcement
from src.bot.ui import strings
from src.bot.utils import notifier
from src.db import Database
from src.db.models import Event


async def set_next_event(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    db: Database = manager.middleware_data["db"]

    # Таймаут рассылки анонсов
    if await throttle_announcement(manager.middleware_data["settings"]):
        pass
    else:
        await callback.answer(strings.errors.announce_too_fast, show_alert=True)
        return

    # Получаем текущее и следующее выступления, снимаем флаг с текущего
    current_event = await db.event.get_current()
    if current_event:
        next_event = await db.event.get_next(current_event)
        if not next_event:
            await callback.answer("👏 Выступления закончились!", show_alert=True)
            return
        current_event.current = None
        await db.session.flush([current_event])
    else:
        next_event = await db.event.get_by_position(1)

    # Отмечаем следующее как текущее
    next_event.current = True
    await db.session.commit()

    # Выводим подтверждение
    await callback.answer(
        f"✅ {next_event.participant.title if next_event.participant else next_event.title}"
    )

    # Запускаем проверку подписок
    asyncio.create_task(
        notifier.proceed_subscriptions(bot=callback.bot, send_global_announcement=True)
    )

    # Отправляем пользователя на страницу со текущим выступлением
    await set_current_schedule_page(manager, next_event.id)
