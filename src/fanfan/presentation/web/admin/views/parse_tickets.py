import logging
from typing import TYPE_CHECKING

from fastapi import Request, UploadFile
from sqladmin import BaseView, expose
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.parsers import parse_tickets

if TYPE_CHECKING:
    from dishka import AsyncContainer

logger = logging.getLogger(__name__)


class ParseTicketsView(BaseView):
    name = "Парсинг билетов"
    icon = "fa-solid fa-file-import"

    @expose("/parse_tickets", methods=["GET", "POST"])
    async def plan_parse(self, request: Request):
        if request.method == "GET":
            return await self.templates.TemplateResponse(request, "parse_tickets.html")
        form = await request.form()
        file: UploadFile = form["file"]
        container: AsyncContainer = request.state.dishka_container
        session = await container.get(AsyncSession)
        async with session:
            try:
                await parse_tickets(file.file, session)
            except Exception as e:
                await container.close()
                logger.exception("Error while parsing plan")
                return await self.templates.TemplateResponse(
                    request,
                    "parse_tickets.html",
                    context={"error": repr(e)},
                )
        return await self.templates.TemplateResponse(
            request,
            "parse_tickets.html",
            context={"success": True},
        )
