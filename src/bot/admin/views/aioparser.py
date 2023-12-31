from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import Request, UploadFile
from sqladmin import BaseView, expose
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.structures import UserRole
from src.db import Database
from src.db.database import create_session_pool


async def parse(path: Path, session: AsyncSession):
    db = Database(session)
    # Парсинг номинаций
    new_nominations = []
    df = pd.read_excel(path, sheet_name="nominations")
    df.replace({np.nan: None}, inplace=True)
    for index, row in df.iterrows():
        nomination = await db.nomination.get(row["id"])
        if not nomination:
            new_nomination = await db.nomination.new(
                id=row["id"],
                title=row["title"],
                votable=row["votable"],
            )
            print(f"Added new nomination {new_nomination.id}")
            new_nominations.append(new_nomination)
    await db.session.flush(new_nominations)
    # Парсинг участников
    new_participants = []
    df = pd.read_excel(path, sheet_name="participants")
    df.replace({np.nan: None}, inplace=True)
    for index, row in df.iterrows():
        participant = await db.participant.get_by_title(row["title"])
        if not participant:
            nomination = await db.nomination.get(row["nomination_id"])
            new_participant = await db.participant.new(
                title=row["title"],
                nomination=nomination,
            )
            print(f"Added new participant {new_participant.title}")
            new_participants.append(new_participant)
    await db.session.flush(new_participants)
    # Парсинг билетов
    new_tickets = []
    df = pd.read_excel(path, sheet_name="tickets")
    df.replace({np.nan: None}, inplace=True)
    for index, row in df.iterrows():
        # ticket = db.session.execute(
        #     select(Ticket).where(func.lower(Ticket.id) == row["id"])
        # ).scalar_one_or_none()
        ticket = await db.ticket.get(row["id"])
        if not ticket:
            new_ticket = await db.ticket.new(
                id=row["id"],
                role=UserRole(row["role"]),
            )
            print(f"Added new ticket {new_ticket.id}")
            new_tickets.append(new_ticket)
    await db.session.flush(new_tickets)
    await db.session.commit()
    return {
        "new_nominations_count": len(new_nominations),
        "new_participants_count": len(new_participants),
        "new_tickets_count": len(new_tickets),
    }


class AioParserView(BaseView):
    name = "Парсинг"
    category = "Парсинг"
    icon = "fa-solid fa-file-import"

    @expose("/aioparser", methods=["GET", "POST"])
    async def plan_parse(self, request: Request):
        if request.method == "GET":
            return await self.templates.TemplateResponse(request, "aioparser.html")
        form = await request.form()
        file: UploadFile = form["file"]
        await file.seek(0)
        content = await file.read()
        path = Path(__file__).parent.joinpath(file.filename)
        with open(path, "wb") as f:
            f.write(content)
        session_pool = create_session_pool()
        async with session_pool() as session:
            await parse(path, session)
        return self.templates.TemplateResponse(
            request,
            "aioparser.html",
        )
