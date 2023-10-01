import flask
import flask_login as login
from flask import request
from flask_admin import Admin, BaseView, expose
from flask_admin.menu import MenuLink
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired

from src.db.models import (
    Achievement,
    Event,
    Nomination,
    Participant,
    ReceivedAchievement,
    Ticket,
    Transaction,
    User,
    Vote,
)
from src.panel import db
from src.panel.views.model_views import (
    AchievementView,
    EventView,
    NominationView,
    ParticipantView,
    ReceivedAchievementView,
    TicketView,
    TransactionView,
    UserView,
    VoteView,
)


class PhotoForm(FlaskForm):
    csrf_enabled = False
    file = FileField(validators=[FileRequired()])


class ParseC2View(BaseView):
    def is_accessible(self):
        return login.current_user.is_authenticated

    @expose("/", methods=["GET", "POST"])
    def parse_c2(self):
        form = PhotoForm()
        if request.method == "POST":
            flask.flash("POST", category="warning")
            return self.render("parse_c2.html", form=form)
        user = db.session.get(User, 517108)
        flask.flash(user.username, category="warning")
        return self.render("parse_c2.html", form=form)


class LogoutMenuLink(MenuLink):
    def is_accessible(self):
        return login.current_user.is_authenticated


def add_views(db: SQLAlchemy, admin: Admin):
    admin.add_views(TicketView(Ticket, db.session, "Билеты", "Пользователи"))
    admin.add_views(UserView(User, db.session, "Пользователи", "Пользователи"))
    admin.add_views(
        AchievementView(Achievement, db.session, "Список достижений", "Достижения")
    )
    admin.add_views(
        ReceivedAchievementView(
            ReceivedAchievement, db.session, "Полученные достижения", "Достижения"
        )
    )
    admin.add_views(EventView(Event, db.session, "Расписание", "Программа"))
    admin.add_views(ParticipantView(Participant, db.session, "Участники", "Программа"))
    admin.add_views(NominationView(Nomination, db.session, "Номинации", "Программа"))
    admin.add_views(VoteView(Vote, db.session, "Голосование", "Программа"))
    admin.add_views(TransactionView(Transaction, db.session, "Транзакции"))
    admin.add_view(
        ParseC2View(name="Парсинг C2", endpoint="parse_c2", category="Парсинг")
    )
    admin.add_link(LogoutMenuLink(name="Выйти", category="", url="/logout"))
