import time

from aiogram import Bot, Router, types
from aiogram.filters import Text
from aiogram.fsm.context import FSMContext

from bot.ui import menus, keyboards, strings
from bot.handlers import states
from bot.db import requests
from bot.config import conf
from bot.db.models import User, Settings, Performance

from sqlalchemy.ext.asyncio import AsyncSession

announcement_timestamp = 0

router = Router(name='callbacks_router')


@router.callback_query(Text(startswith="send_announcement"), flags={'allowed_roles': ['org', 'helper']})
async def send_announcement(callback: types.CallbackQuery, bot: Bot, session: AsyncSession):
    global announcement_timestamp
    timestamp = time.time()
    if (timestamp - announcement_timestamp) > 5:
        announcement_timestamp = timestamp
        position = int(callback.data.split()[1])
        results = await requests.fetch_performances(session, current=True)
        for result in results:
            result.current = False
        result = await requests.fetch_performances(session, position=position)
        current_event: Performance = result.one_or_none()
        if current_event:
            current_event.current = True
        await session.commit()
        # users = await requests.fetch_users(session, notifications_enabled=True)
        # if users is None:
        #     await callback.answer()
        #     return
        text = callback.message.html_text + f"\n<i>Отправил @{callback.from_user.username} ({callback.from_user.id})</i>"
        # for user in users:
        #     if user.tg_id:
        #         await bot.send_message(user.tg_id, text)
        await bot.send_message(conf.channel_id, text)
        await callback.message.delete()
        await callback.answer()
    else:
        await callback.answer(strings.announcement_too_fast, show_alert=True)


@router.callback_query(Text("main_menu"))
async def open_main_menu(callback: types.CallbackQuery, user: User):
    await menus.main_menu(callback.message, user)
    await callback.answer()


@router.callback_query(Text("switch_notifications"))
async def switch_notifications(callback: types.CallbackQuery, user: User, session: AsyncSession):
    user.notifications_enabled = not user.notifications_enabled
    await session.commit()
    await callback.message.edit_reply_markup(reply_markup=keyboards.main_menu_kb(user.role,
                                                                                 user.notifications_enabled))
    await callback.answer()


@router.callback_query(Text("nominations_menu"))
async def open_nominations_menu(callback: types.CallbackQuery, session: AsyncSession):
    settings: Settings = await requests.fetch_settings(session)
    if settings.voting_enabled:
        await menus.nominations_menu(callback.message, session)
        await callback.answer()
    else:
        await callback.answer(strings.voting_disabled, show_alert=True)


@router.callback_query(Text("helper_menu"), flags={'allowed_roles': ['helper', 'org']})
async def open_helper_menu(callback: types.CallbackQuery):
    await menus.helper_menu(callback.message)
    await callback.answer()


@router.callback_query(Text("org_menu"), flags={'allowed_roles': ['org']})
async def open_org_menu(callback: types.CallbackQuery, session: AsyncSession):
    settings = await requests.fetch_settings(session)
    await menus.org_menu(callback.message, settings)
    await callback.answer()


@router.callback_query(Text(startswith="category"))
async def open_voting_menu(callback: types.CallbackQuery, session: AsyncSession):
    category = callback.data.split()[1]
    await menus.voting_menu(session, callback.message, int(category))
    await callback.answer()


@router.callback_query(Text("delete_message"))
async def delete_message(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.answer()


@router.callback_query(Text("announce_mode"), flags={'allowed_roles': ['helper', 'org']})
async def announce_mode(callback: types.CallbackQuery, state: FSMContext):
    kb = keyboards.announce_mode_kb()
    await callback.message.answer(text=strings.announce_mode_guide, reply_markup=kb)
    await state.set_state(states.Modes.AnnounceMode)
    await callback.answer()


@router.callback_query(Text("switch_voting"), flags={'allowed_roles': ['org']})
async def announce_mode(callback: types.CallbackQuery, session: AsyncSession):
    settings: Settings = await requests.fetch_settings(session)
    settings.voting_enabled = not settings.voting_enabled
    await session.commit()
    await callback.message.edit_reply_markup(reply_markup=keyboards.org_menu_kb(settings))
    await callback.answer()

