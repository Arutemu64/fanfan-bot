from dataclasses import dataclass

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from starlette.responses import JSONResponse

from fanfan.adapters.api.ticketscloud.dto.order import Order
from fanfan.adapters.api.ticketscloud.importer import TCloudImporter

tcloud_webhook_router = APIRouter()


@dataclass(slots=True, frozen=True)
class TCloudWebhookPayload:
    data: Order
    type: str  # TODO Enforce possible types later


@tcloud_webhook_router.post("/tcloud_webhook")
@inject
async def order_change(
    payload: TCloudWebhookPayload,
    tcloud_importer: FromDishka[TCloudImporter],
) -> JSONResponse:
    added_tickets = await tcloud_importer.proceed_order(payload.data)
    data = {"added_tickets": added_tickets}
    return JSONResponse(content=data, status_code=200)
