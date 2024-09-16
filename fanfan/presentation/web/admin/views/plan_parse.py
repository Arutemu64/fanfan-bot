import logging
import typing

from fastapi import Request, UploadFile
from openpyxl import load_workbook
from sqladmin import BaseView, expose
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.infrastructure.db.models import Event, Nomination, Participant

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer

logger = logging.getLogger(__name__)


async def proceed_plan(file: typing.BinaryIO, session: AsyncSession) -> None:
    # Constraints must be deferred, so we can swap ids and order
    await session.execute(text("SET CONSTRAINTS ALL DEFERRED"))
    events_to_delete = list(await session.scalars(select(Event)))
    order = 1.0
    wb = load_workbook(file)
    ws = wb.worksheets[0]
    for row in ws.iter_rows():
        id_ = row[1]
        data = row[2]
        if id_.value:
            participant_title = data.value.split(", ", 1)[1]
            participant = await session.scalar(
                select(Participant)
                .where(Participant.title == participant_title)
                .limit(1)
                .options(joinedload(Participant.event)),
            )
            if participant:
                if participant.event:
                    events_to_delete.remove(participant.event)
                    participant.event.id = id_.value
                    participant.event.order = order
                else:
                    participant.event = Event(
                        id=id_.value,
                        order=order,
                        title=participant.title,
                    )
            else:
                nomination_id = data.value.split()[0]
                nomination = await session.get(Nomination, nomination_id)
                if not nomination:
                    nomination = Nomination(
                        id=nomination_id,
                        title=ws.cell(data.row - 1, data.column).value,
                    )
                    session.add(nomination)
                participant = Participant(
                    title=participant_title,
                    nomination=nomination,
                    event=Event(
                        id=id_.value,
                        order=order,
                        title=participant_title,
                    ),
                )
                session.add(participant)
            order += 1.0
    for e in events_to_delete:
        await session.delete(e)


class PlanParseView(BaseView):
    name = "Импорт расписания (C2)"
    icon = "fa-solid fa-file-import"

    @expose("/plan_parse", methods=["GET", "POST"])
    async def plan_parse(self, request: Request):
        if request.method == "GET":
            return await self.templates.TemplateResponse(request, "plan_parse.html")
        form = await request.form()
        file: UploadFile = form["file"]
        container: AsyncContainer = request.state.dishka_container
        session = await container.get(AsyncSession)
        async with session:
            try:
                await proceed_plan(file.file, session)
                await session.commit()
            except Exception as e:
                await container.close()
                logger.exception("Error when parsing plan")
                return await self.templates.TemplateResponse(
                    request,
                    "plan_parse.html",
                    context={"error": repr(e)},
                )
        return await self.templates.TemplateResponse(
            request,
            "plan_parse.html",
            context={"success": True},
        )
