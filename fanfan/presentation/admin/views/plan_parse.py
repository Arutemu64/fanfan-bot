import logging
from pathlib import Path

from dishka import make_async_container
from fastapi import Request, UploadFile
from openpyxl import load_workbook
from sqladmin import BaseView, expose
from sqlalchemy import text

from fanfan.common import TEMP_DIR
from fanfan.infrastructure.db import UnitOfWork
from fanfan.infrastructure.db.models import Event, Nomination, Participant
from fanfan.infrastructure.di.config import ConfigProvider
from fanfan.infrastructure.di.db import DbProvider

logger = logging.getLogger(__name__)


async def proceed_plan(path: Path, uow: UnitOfWork):
    # Drop schedule first
    await uow.session.execute(text("TRUNCATE TABLE schedule CASCADE"))
    await uow.session.execute(
        text("ALTER SEQUENCE subscriptions_id_seq RESTART WITH 1"),
    )
    await uow.session.execute(text("ALTER SEQUENCE schedule_id_seq RESTART WITH 1"))
    await uow.session.execute(
        text("ALTER SEQUENCE schedule_order_seq RESTART WITH 1"),
    )
    wb = load_workbook(path)
    ws = wb.worksheets[0]
    for row in ws.iter_rows():
        id_ = row[1]
        data = row[2]
        if id_.value:
            participant_title = data.value.split(", ", 1)[1]
            participant = await uow.participants.get_participant_by_title(
                participant_title
            )
            if not participant:
                nomination_id = data.value.split()[0]
                nomination = await uow.nominations.get_nomination(nomination_id)
                if not nomination:
                    nomination = Nomination(
                        id=nomination_id,
                        title=ws.cell(data.row - 1, data.column).value,
                    )
                    uow.session.add(nomination)
                participant = Participant(
                    title=participant_title,
                    nomination=nomination,
                )
                uow.session.add(participant)
            uow.session.add(
                Event(
                    id=id_.value,
                    title=participant.title,
                    participant=participant,
                )
            )


class PlanParseView(BaseView):
    name = "Импорт расписания (C2)"
    icon = "fa-solid fa-file-import"

    @expose("/plan_parse", methods=["GET", "POST"])
    async def plan_parse(self, request: Request):
        if request.method == "GET":
            return await self.templates.TemplateResponse(request, "plan_parse.html")
        form = await request.form()
        file: UploadFile = form["file"]
        await file.seek(0)
        content = await file.read()
        path = TEMP_DIR.joinpath(file.filename)
        with open(path, "wb") as f:
            f.write(content)
        container = make_async_container(DbProvider(), ConfigProvider())
        async with container() as request_container:
            uow = await request_container.get(UnitOfWork)
            async with uow:
                try:
                    await proceed_plan(path, uow)
                    await uow.commit()
                except Exception as e:
                    await container.close()
                    logger.exception(e)
                    return await self.templates.TemplateResponse(
                        request,
                        "plan_parse.html",
                        context={"error": repr(e)},
                    )
        await container.close()
        return await self.templates.TemplateResponse(
            request,
            "plan_parse.html",
            context={"success": True},
        )
