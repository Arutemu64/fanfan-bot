from pathlib import Path

import pandas as pd
from fastapi import Request, UploadFile
from sqladmin import BaseView, expose
from sqlalchemy.exc import IntegrityError

from fanfan import TEMP_DIR
from fanfan.common.enums import UserRole
from fanfan.infrastructure.db.main import create_session_pool
from fanfan.infrastructure.db.models import Nomination, Participant, Ticket
from fanfan.infrastructure.db.uow import UnitOfWork


async def parse(path: Path, uow: UnitOfWork):
    # Парсинг номинаций
    df = pd.read_excel(
        path,
        sheet_name="nominations",
        converters={
            "id": str,
            "title": str,
            "votable": bool,
        },
    )
    for index, row in df.iterrows():
        try:
            async with uow.session.begin_nested():
                nomination = Nomination(
                    id=row["id"], title=row["title"], votable=row["votable"]
                )
                uow.session.add(nomination)
        except IntegrityError as e:
            nomination = await uow.nominations.get_nomination(row["id"])
            if not nomination:
                raise e
    # Парсинг участников
    df = pd.read_excel(path, sheet_name="participants")
    for index, row in df.iterrows():
        try:
            async with uow.session.begin_nested():
                participant = Participant(
                    title=row["title"], nomination_id=row["nomination_id"]
                )
                uow.session.add(participant)
        except IntegrityError as e:
            participant = await uow.participants.get_participant_by_title(row["title"])
            if not participant:
                raise e
    await uow.commit()
    # Парсинг билетов
    df = pd.read_excel(
        path,
        sheet_name="tickets",
        converters={
            "id": str,
            "role": UserRole,
        },
    )
    for index, row in df.iterrows():
        try:
            async with uow.session.begin_nested():
                ticket = Ticket(id=row["id"], role=row["role"])
                uow.session.add(ticket)
        except IntegrityError as e:
            ticket = await uow.tickets.get_ticket(row["id"])
            if not ticket:
                raise e


class AioParserView(BaseView):
    name = "Общий парсинг"
    icon = "fa-solid fa-file-import"

    @expose("/aioparser", methods=["GET", "POST"])
    async def plan_parse(self, request: Request):
        if request.method == "GET":
            return await self.templates.TemplateResponse(request, "aioparser.html")
        form = await request.form()
        file: UploadFile = form["file"]
        await file.seek(0)
        content = await file.read()
        path = TEMP_DIR.joinpath(file.filename)
        with open(path, "wb") as f:
            f.write(content)
        session_pool = create_session_pool()
        uow = UnitOfWork(session_pool())
        async with uow:
            try:
                await parse(path, uow)
                await uow.commit()
            except Exception as e:
                return await self.templates.TemplateResponse(
                    request, "aioparser.html", context={"error": repr(e)}
                )
        return await self.templates.TemplateResponse(
            request, "aioparser.html", context={"success": True}
        )
