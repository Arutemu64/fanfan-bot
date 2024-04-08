from pathlib import Path

import pandas as pd
from dishka import make_async_container
from fastapi import Request, UploadFile
from sqladmin import BaseView, expose
from sqlalchemy.exc import IntegrityError

from fanfan.common import TEMP_DIR
from fanfan.common.enums import UserRole
from fanfan.infrastructure.db.models import Nomination, Participant, Ticket
from fanfan.infrastructure.db.uow import UnitOfWork
from fanfan.infrastructure.di.config import ConfigProvider
from fanfan.infrastructure.di.db import DbProvider


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
                    id=row["id"],
                    title=row["title"],
                    votable=row["votable"],
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
                    title=row["title"],
                    nomination_id=row["nomination_id"],
                )
                uow.session.add(participant)
        except IntegrityError as e:
            participant = await uow.participants.get_participant_by_title(row["title"])
            if not participant:
                raise e
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
        container = make_async_container(DbProvider(), ConfigProvider())
        async with container() as request_container:
            uow = await request_container.get(UnitOfWork)
            async with uow:
                try:
                    await parse(path, uow)
                    await uow.commit()
                except Exception as e:
                    await container.close()
                    return await self.templates.TemplateResponse(
                        request,
                        "aioparser.html",
                        context={"error": repr(e)},
                    )
        await container.close()
        return await self.templates.TemplateResponse(
            request,
            "aioparser.html",
            context={"success": True},
        )
