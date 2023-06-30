from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import requests
from bot.db.models import User

async def service_message(session: AsyncSession, bot: Bot, text=''):
    final_text = f"""<i>🤖 Служебное уведомление</i>\n\n{text}\n\n<i>Это сообщение видят только организаторы</i>"""
    orgs = await requests.get_users(session, User.role == 'org')
    for org in orgs:
        if org.tg_id:
            await bot.send_message(org.tg_id, final_text)
