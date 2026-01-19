from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from starlette.responses import JSONResponse

from fanfan.application.tickets.proceed_tcloud_order import (
    ProceedTCloudWebhook,
    TCloudWebhookDTO,
)

tcloud_webhook_router = APIRouter()


@tcloud_webhook_router.post("/tcloud_webhook")
@inject
async def order_change(
    payload: TCloudWebhookDTO,
    proceed_tcloud_webhook: FromDishka[ProceedTCloudWebhook],
) -> JSONResponse:
    result = await proceed_tcloud_webhook(payload)
    data = {"new_tickets_count": result.new_tickets_count}
    return JSONResponse(content=data, status_code=200)
