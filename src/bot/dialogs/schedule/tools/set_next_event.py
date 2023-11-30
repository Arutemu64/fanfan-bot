import asyncio

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button

from src.bot.dialogs.schedule.common import set_schedule_page
from src.bot.dialogs.schedule.tools import notifier
from src.bot.dialogs.schedule.tools.common import (
    throttle_announcement,
)
from src.bot.structures import UserRole
from src.bot.ui import strings
from src.db import Database
from src.db.models import DBUser


async def set_next_event(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    db: Database = manager.middleware_data["db"]
    user: DBUser = manager.middleware_data["current_user"]

    # Проверяем права
    if user.role < UserRole.HELPER:
        await callback.answer(strings.errors.access_denied, show_alert=True)
        return

    # Таймаут рассылки анонсов
    settings = await db.settings.get()
    time_left = await throttle_announcement(db, settings)
    if not time_left == 0:
        await callback.answer(
            strings.errors.announce_too_fast.format(
                announcement_timeout=settings.announcement_timeout,
                time_left=time_left,
            ),
            show_alert=True,
        )
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
    await callback.answer(f"✅ {next_event.title}")

    # Запускаем проверку подписок
    asyncio.create_task(
        notifier.proceed_subscriptions(
            arq=manager.middleware_data["arq"], send_global_announcement=True
        )
    )

    # Отправляем пользователя на страницу со текущим выступлением
    await set_schedule_page(manager, next_event)
