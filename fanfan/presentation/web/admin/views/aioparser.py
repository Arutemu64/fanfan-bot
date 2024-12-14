import logging
from typing import TYPE_CHECKING, BinaryIO

import pandas as pd
from fastapi import Request, UploadFile
from sqladmin import BaseView, expose
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import DBNomination, DBParticipant, DBTicket
from fanfan.core.models.user import UserRole

if TYPE_CHECKING:
    from dishka import AsyncContainer

logger = logging.getLogger(__name__)


async def parse(file: BinaryIO, session: AsyncSession) -> None:
    # Парсинг номинаций
    nominations_df = pd.read_excel(
        file,
        sheet_name="nominations",
        converters={
            "id": str,
            "title": str,
            "is_votable": bool,
        },
    )
    for _index, row in nominations_df.iterrows():
        try:
            async with session.begin_nested():
                session.add(
                    DBNomination(
                        id=row["id"],
                        title=row["title"],
                        is_votable=row["is_votable"],
                    ),
                )
        except IntegrityError:
            nomination = await session.get(DBNomination, row["id"])
            if not nomination:
                raise
    # Парсинг участников
    participants_df = pd.read_excel(file, sheet_name="participants")
    for _index, row in participants_df.iterrows():
        try:
            async with session.begin_nested():
                session.add(
                    DBParticipant(
                        title=row["title"],
                        nomination_id=row["nomination_id"],
                    ),
                )
        except IntegrityError:
            participant = await session.scalar(
                select(DBParticipant).where(DBParticipant.title == row["title"]),
            )
            if not participant:
                raise
    # Парсинг билетов
    tickets_df = pd.read_excel(
        file,
        sheet_name="tickets",
        converters={
            "id": str,
            "role": UserRole,
        },
    )
    for _index, row in tickets_df.iterrows():
        try:
            async with session.begin_nested():
                session.add(DBTicket(id=row["id"], role=row["role"]))
        except IntegrityError:
            ticket = await session.get(DBTicket, row["id"])
            if not ticket:
                raise


class AioParserView(BaseView):
    name = "Общий парсинг"
    icon = "fa-solid fa-file-import"

    @expose("/aioparser", methods=["GET", "POST"])
    async def plan_parse(self, request: Request):
        if request.method == "GET":
            return await self.templates.TemplateResponse(request, "aioparser.html")
        form = await request.form()
        file: UploadFile = form["file"]
        container: AsyncContainer = request.state.dishka_container
        session = await container.get(AsyncSession)
        async with session:
            try:
                await parse(file.file, session)
                await session.commit()
            except Exception as e:
                await container.close()
                logger.exception("Error while parsing plan")
                return await self.templates.TemplateResponse(
                    request,
                    "aioparser.html",
                    context={"error": repr(e)},
                )
        return await self.templates.TemplateResponse(
            request,
            "aioparser.html",
            context={"success": True},
        )
