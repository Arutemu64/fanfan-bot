from pathlib import Path

import flask
import flask_login
import numpy as np
import pandas as pd
from flask_admin import BaseView, expose
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from sqlalchemy import func, select

from src.db.models import Nomination, Participant, Ticket
from src.panel import db


def parse(path: Path):
    # Парсинг номинаций
    new_nominations = []
    df = pd.read_excel(path, sheet_name="nominations")
    df.replace({np.nan: None}, inplace=True)
    for index, row in df.iterrows():
        nomination = db.session.get(Nomination, row["id"])
        if not nomination:
            new_nomination = Nomination(
                id=row["id"],
                title=row["title"],
                votable=row["votable"],
            )
            db.session.add(new_nomination)
            print(f"Added new nomination {new_nomination.id}")
            new_nominations.append(new_nomination)
    db.session.flush(new_nominations)
    # Парсинг участников
    new_participants = []
    df = pd.read_excel(path, sheet_name="participants")
    df.replace({np.nan: None}, inplace=True)
    for index, row in df.iterrows():
        participant = db.session.execute(
            select(Participant).where(Participant.title == row["title"])
        ).scalar_one_or_none()
        if not participant:
            new_participant = Participant(
                title=row["title"],
                nomination_id=row["nomination_id"],
            )
            db.session.add(new_participant)
            print(f"Added new participant {new_participant.title}")
            new_participants.append(new_participant)
    db.session.flush(new_participants)
    # Парсинг билетов
    new_tickets = []
    df = pd.read_excel(path, sheet_name="tickets")
    df.replace({np.nan: None}, inplace=True)
    for index, row in df.iterrows():
        ticket = db.session.execute(
            select(Ticket).where(func.lower(Ticket.id) == row["id"])
        ).scalar_one_or_none()
        if not ticket:
            new_ticket = Ticket(
                id=row["id"],
                role=row["role"],
            )
            db.session.add(new_ticket)
            print(f"Added new ticket {new_ticket.id}")
            new_tickets.append(new_ticket)
    db.session.flush(new_tickets)
    db.session.commit()
    return {
        "new_nominations_count": len(new_nominations),
        "new_participants_count": len(new_participants),
        "new_tickets_count": len(new_tickets),
    }


class AioParserForm(FlaskForm):
    csrf_enabled = False
    file = FileField(validators=[FileRequired(), FileAllowed(["xlsx"], "xlsx only!")])


class AioParserView(BaseView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated

    @expose("/", methods=["GET", "POST"])
    def parse_c2(self):
        form = AioParserForm()
        if form.validate_on_submit():
            f = form.file.data
            path = Path(__file__).parent.joinpath(f.filename)
            f.save(path)
            results = parse(path)
            flask.flash(
                f"Было добавлено {results['new_nominations_count']} новых номинаций, "
                f"{results['new_participants_count']} новых участников, "
                f"{results['new_tickets_count']} новых билетов",
                category="info",
            )
            return self.render("aioparser.html", form=form)
        return self.render("aioparser.html", form=form)
