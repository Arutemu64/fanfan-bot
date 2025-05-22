from dataclasses import dataclass
from enum import StrEnum

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, HTTPException
from starlette.responses import JSONResponse

from fanfan.adapters.api.ticketscloud.config import TCloudConfig
from fanfan.adapters.api.ticketscloud.dto.order import Order
from fanfan.adapters.api.ticketscloud.importer import TCloudImporter

tcloud_webhook_router = APIRouter()


class TCloudWebhookType(StrEnum):
    ORDER_CREATED = "order_created"
    ORDER_IN_PROGRESS = "order_in_progress"
    ORDER_DONE = "order_done"
    ORDER_CANCELLED = "order_cancelled"
    ORDER_EXPIRED = "order_expired"


@dataclass(slots=True, frozen=True)
class TCloudWebhookPayload:
    data: Order
    type: TCloudWebhookType


@tcloud_webhook_router.post("/tcloud_webhook")
@inject
async def order_change(
    payload: TCloudWebhookPayload,
    tcloud_importer: FromDishka[TCloudImporter],
    config: FromDishka[TCloudConfig | None],
) -> JSONResponse:
    if config:
        added_tickets = await tcloud_importer.proceed_order(payload.data)
        data = {"added_tickets": added_tickets}
        return JSONResponse(content=data, status_code=200)
    raise HTTPException(status_code=500, detail="TCloud config not provided")
