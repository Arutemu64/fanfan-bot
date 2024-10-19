from aiogram.utils.web_app import safe_parse_webapp_init_data
from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Request
from starlette.responses import JSONResponse

from fanfan.infrastructure.auth.utils.token import JwtTokenProcessor
from fanfan.infrastructure.config_reader import BotConfig


@inject
async def webapp_auth(
    request: Request,
    config: FromDishka[BotConfig],
    token_processor: FromDishka[JwtTokenProcessor],
):
    data = await request.form()
    # Auth
    try:
        web_app_init_data = safe_parse_webapp_init_data(
            token=config.token.get_secret_value(),
            init_data=data["_auth"],
        )
        token = token_processor.create_access_token(web_app_init_data.user.id)
        request.session["token"] = token
    except ValueError:
        return JSONResponse({"ok": False, "err": "Unauthorized"}, status_code=401)
