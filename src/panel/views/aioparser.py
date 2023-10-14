from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import Request, UploadFile
from sqladmin import BaseView, expose
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import Database
from src.db.models import Nomination, Participant, Ticket
from src.panel import engine


async def parse(path: Path):
    db = Database(AsyncSession(bind=engine, expire_on_commit=False))
    # Парсинг номинаций
    new_nominations = []
    df = pd.read_excel(path, sheet_name="nominations")
    df.replace({np.nan: None}, inplace=True)
    for index, row in df.iterrows():
        nomination = await db.nomination.get(row["id"])
        if not nomination:
            new_nomination = Nomination(
                id=row["id"],
                title=row["title"],
                votable=row["votable"],
            )
            db.session.add(new_nomination)
            print(f"Added new nomination {new_nomination.id}")
            new_nominations.append(new_nomination)
    await db.session.flush(new_nominations)
    # Парсинг участников
    new_participants = []
    df = pd.read_excel(path, sheet_name="participants")
    df.replace({np.nan: None}, inplace=True)
    for index, row in df.iterrows():
        participant = await db.participant._get_by_where(
            Participant.title == row["title"]
        )
        if not participant:
            new_participant = Participant(
                title=row["title"],
                nomination_id=row["nomination_id"],
            )
            db.session.add(new_participant)
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
        ticket = await db.ticket.exists(row["id"])
        if not ticket:
            new_ticket = Ticket(
                id=row["id"],
                role=row["role"],
            )
            db.session.add(new_ticket)
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
            print("GET")
            return self.templates.TemplateResponse(
                "aioparser.html", context={"request": request}
            )
        form = await request.form()
        file: UploadFile = form["file"]
        await file.seek(0)
        content = await file.read()
        path = Path(__file__).parent.joinpath(file.filename)
        with open(path, "wb") as f:
            f.write(content)
        await parse(path)
        return self.templates.TemplateResponse(
            "aioparser.html", context={"request": request}
        )
