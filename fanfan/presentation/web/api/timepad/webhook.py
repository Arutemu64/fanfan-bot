from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Depends

from fanfan.adapters.config_reader import TimepadConfig
from fanfan.adapters.timepad.dto.order import RegistrationOrderResponse
from fanfan.application.utils.proceed_order import (
    ProceedOrder,
    ProceedOrderResult,
)
from fanfan.presentation.web.api.timepad.utils import verify_timepad_signature

timepad_webhook_router = APIRouter()


@timepad_webhook_router.post(
    "/webhook",
    dependencies=[Depends(verify_timepad_signature)],
)
@inject
async def order_change(
    data: RegistrationOrderResponse,
    interactor: FromDishka[ProceedOrder],
    config: FromDishka[TimepadConfig],
) -> ProceedOrderResult | None:
    if data.event.id == config.event_id:
        return await interactor(data)
    return None
