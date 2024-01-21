from aiogram import Bot, Dispatcher
from aiogram.types import Update
from fastapi import APIRouter, Request

webhook_router = APIRouter(prefix="/webhook")


@webhook_router.post("")
async def handle_webhook_update(request: Request):
    dp: Dispatcher = request.app.state.dp
    bot: Bot = request.app.state.bot
    telegram_update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, telegram_update)
