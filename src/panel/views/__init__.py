import flask_login
from flask_admin import Admin
from flask_admin.menu import MenuLink
from flask_sqlalchemy import SQLAlchemy

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
from src.panel.views.aioparser import AioParserView
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
from src.panel.views.plan_parser import PlanParserView


class LogoutMenuLink(MenuLink):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated


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
        PlanParserView(
            name="Парсинг расписания (Cosplay2)",
            endpoint="plan_parse_c2",
            category="Парсинг",
        )
    )
    admin.add_view(
        AioParserView(
            name="Универсальный парсинг", endpoint="aioparser", category="Парсинг"
        )
    )
    admin.add_link(LogoutMenuLink(name="Выйти", category="", url="/logout"))
