from aiogram.utils.web_app import safe_parse_webapp_init_data
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Request
from starlette.responses import JSONResponse

from fanfan.adapters.auth.utils.token import JwtTokenProcessor
from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.core.vo.telegram import TelegramUserId
from fanfan.presentation.tgbot.config import BotConfig


@inject
async def webapp_auth(
    request: Request,
    config: FromDishka[BotConfig],
    token_processor: FromDishka[JwtTokenProcessor],
    users_repo: FromDishka[UsersRepository],
):
    data = await request.json()
    try:
        web_app_init_data = safe_parse_webapp_init_data(
            token=config.token.get_secret_value(),
            init_data=data["_auth"],
        )
        user = await users_repo.get_user_by_tg_id(
            TelegramUserId(web_app_init_data.user.id)
        )
        token = token_processor.create_access_token(user.id)
        request.session["token"] = token
    except ValueError:
        return JSONResponse({"ok": False, "err": "Unauthorized"}, status_code=401)
