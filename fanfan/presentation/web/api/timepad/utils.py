import hashlib
import hmac
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import Header, HTTPException, Request

from fanfan.adapters.config_reader import TimepadConfig


@inject
async def verify_timepad_signature(
    request: Request,
    config: FromDishka[TimepadConfig | None],
    x_hub_signature: Annotated[str, Header()],
) -> None:
    expected_signature = hmac.new(
        key=config.secret.get_secret_value().encode(),
        msg=await request.body(),
        digestmod=hashlib.sha1,
    )
    if f"sha1={expected_signature.hexdigest()}" != x_hub_signature:
        raise HTTPException(status_code=403, detail="Signature verification failed")
