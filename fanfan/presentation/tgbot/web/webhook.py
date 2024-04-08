from aiogram import Bot, Dispatcher
from aiogram.types import Update
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Request

webhook_router = APIRouter(prefix="/webhook")


@webhook_router.post("")
@inject
async def handle_webhook_update(
    request: Request,
    dp: FromDishka[Dispatcher],
    bot: FromDishka[Bot],
):
    telegram_update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, telegram_update)
