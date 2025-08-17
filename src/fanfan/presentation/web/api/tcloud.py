from dataclasses import dataclass
from typing import Annotated

from dishka import FromDishka
from dishka.integrations.fastapi import inject
from fastapi import APIRouter, Body, HTTPException
from starlette.responses import JSONResponse

from fanfan.adapters.api.ticketscloud.config import TCloudConfig
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
    tcloud_importer: FromDishka[TCloudImporter],
    config: FromDishka[TCloudConfig | None],
    payload: Annotated[TCloudWebhookPayload | None, Body()] = None,
) -> JSONResponse:
    # если пришёл пустой POST
    if payload is None:
        return JSONResponse(
            content={"status": "ignored empty webhook"}, status_code=200
        )

    if config:
        added_tickets = await tcloud_importer.proceed_order(payload.data)
        return JSONResponse(content={"added_tickets": added_tickets}, status_code=200)

    raise HTTPException(status_code=500, detail="TCloud config not provided")
