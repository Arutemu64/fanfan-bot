import logging
import typing

from fastapi import Request, UploadFile
from openpyxl import load_workbook
from sqladmin import BaseView, expose
from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.infrastructure.db.models import Event, Nomination, Participant
from fanfan.infrastructure.db.models.block import Block

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer

logger = logging.getLogger(__name__)


async def proceed_plan(file: typing.BinaryIO, session: AsyncSession) -> None:
    # Constraints must be deferred, so we can swap ids and order
    await session.execute(text("SET CONSTRAINTS ALL DEFERRED"))
    # Delete orphaned events later
    events_to_delete = list(await session.scalars(select(Event)))
    # Delete all blocks
    await session.execute(delete(Block))
    await session.flush()
    # Get everything ready
    wb = load_workbook(file)
    ws = wb.worksheets[0]
    current_nomination: Nomination | None = None
    order = 1.0
    for row in ws.iter_rows(min_row=4):
        if row[0].value and row[2].value:  # Block
            title = str(row[2].value)
            block = Block(title=title, start_order=order)
            session.add(block)
            await session.flush([block])
            logger.info("New block %s added", title)
        elif row[2].value and (row[1].value is None):  # Nomination
            title = str(row[2].value)
            # Cut ID from next row
            next_cell = ws.cell(column=row[2].column, row=row[2].row + 1)
            participant_string = str(next_cell.value)
            nomination_id = participant_string.split(" ")[0]
            current_nomination = Nomination(id=nomination_id, title=title)
            current_nomination = await session.merge(current_nomination)
            await session.flush([current_nomination])
            logger.info("New nomination %s added", nomination_id)
        elif row[1].value:  # Participant
            id_ = int(row[1].value)
            data = str(row[2].value)
            participant_title = data.split(", ", 1)[1]
            participant = await session.scalar(
                select(Participant)
                .where(Participant.title == participant_title)
                .limit(1)
                .options(joinedload(Participant.event)),
            )
            if participant:
                if participant.event:
                    events_to_delete.remove(participant.event)
                    participant.event.id = id_
                    participant.event.order = order
                else:
                    participant.event = Event(
                        id=id_,
                        order=order,
                        title=participant.title,
                    )
                await session.flush([participant])
            else:
                participant = Participant(
                    title=participant_title,
                    nomination=current_nomination,
                    event=Event(
                        id=id_,
                        order=order,
                        title=participant_title,
                    ),
                )
                session.add(participant)
                await session.flush([participant])
                logger.info("New participant %s added", participant_title)
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
