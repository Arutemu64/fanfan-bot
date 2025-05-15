import logging
import typing

from fastapi import Request, UploadFile
from sqladmin import BaseView, expose
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.repositories.nominations import NominationsRepository
from fanfan.adapters.db.repositories.participants import ParticipantsRepository
from fanfan.adapters.utils.parsers.parse_schedule import parse_schedule
from fanfan.application.schedule.management.replace_schedule import ReplaceSchedule

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer

logger = logging.getLogger(__name__)


class ParseScheduleView(BaseView):
    name = "Парсинг расписания"
    icon = "fa-solid fa-file-import"

    @expose("/parse_schedule", methods=["GET", "POST"])
    async def plan_parse(self, request: Request):
        if request.method == "GET":
            return await self.templates.TemplateResponse(request, "parse_schedule.html")
        form = await request.form()
        file: UploadFile = form["file"]
        container: AsyncContainer = request.state.dishka_container
        session = await container.get(AsyncSession)
        async with session:
            try:
                await parse_schedule(
                    file.file,
                    replace_schedule=await container.get(ReplaceSchedule),
                    participants_repo=await container.get(ParticipantsRepository),
                    nominations_repo=await container.get(NominationsRepository),
                )
            except Exception as e:
                await container.close()
                logger.exception("Error when parsing plan", exc_info=e)
                return await self.templates.TemplateResponse(
                    request,
                    "parse_schedule.html",
                    context={"error": repr(e)},
                )
        return await self.templates.TemplateResponse(
            request,
            "parse_schedule.html",
            context={"success": True},
        )
