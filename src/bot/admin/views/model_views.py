from sqladmin import ModelView

from src.db.models import (
    Achievement,
    DBUser,
    Event,
    Nomination,
    Participant,
    ReceivedAchievement,
    Ticket,
    Transaction,
    Vote,
)


class TicketAdmin(ModelView, model=Ticket):
    name_plural = "Билеты"
    icon = "fa-solid fa-ticket"
    column_list = [Ticket.id, Ticket.role, Ticket.time_created]
    column_labels = {
        Ticket.id: "Номер билета",
        Ticket.role: "Роль",
        Ticket.time_created: "Время выпуска",
    }
    form_columns = [Ticket.id, Ticket.role]
    form_include_pk = True
    column_searchable_list = [Ticket.id, Ticket.role]


class UserAdmin(ModelView, model=DBUser):
    name_plural = "Пользователи"
    icon = "fa-solid fa-users"
    can_create = False
    column_list = [
        DBUser.id,
        DBUser.username,
        DBUser.role,
        DBUser.achievements_count,
        DBUser.points,
        DBUser.time_created,
        DBUser.received_achievements,
    ]
    column_labels = {
        DBUser.id: "ID",
        DBUser.username: "Имя пользователя",
        DBUser.role: "Роль",
        DBUser.achievements_count: "Достижений получено",
        DBUser.points: "Очков",
        DBUser.time_created: "Время регистрации",
    }
    form_columns = [DBUser.username, DBUser.role]
    column_searchable_list = [DBUser.username, DBUser.role]
    column_sortable_list = [DBUser.achievements_count, DBUser.points]


class AchievementAdmin(ModelView, model=Achievement):
    name_plural = "Достижения"
    icon = "fa-solid fa-trophy"
    column_list = [Achievement.id, Achievement.title, Achievement.description]
    column_labels = {
        Achievement.id: "ID",
        Achievement.title: "Название",
        Achievement.description: "Описание",
    }
    form_excluded_columns = [Achievement.time_created, Achievement.time_updated]


class ReceivedAchievementAdmin(ModelView, model=ReceivedAchievement):
    name_plural = "Полученные достижения"
    icon = "fa-solid fa-star"
    column_list = [
        ReceivedAchievement.user,
        ReceivedAchievement.achievement,
        ReceivedAchievement.time_created,
    ]
    column_labels = {
        ReceivedAchievement.user: "Пользователь",
        ReceivedAchievement.achievement: "Достижение",
        ReceivedAchievement.time_created: "Время получения",
    }
    can_create = False
    can_edit = False


class EventAdmin(ModelView, model=Event):
    name_plural = "Расписание"
    icon = "fa-solid fa-calendar-days"
    column_list = [
        Event.id,
        Event.position,
        Event.real_position,
        Event.title,
        Event.skip,
    ]
    column_labels = {
        Event.id: "ID",
        Event.position: "Позиция",
        Event.real_position: "Позиция (с учётом пропусков)",
        Event.title: "Название",
        Event.participant: "Участник",
        Event.skip: "Пропущено",
    }
    form_columns = {
        Event.participant,
        Event.position,
        Event.title,
        Event.skip,
    }


class ParticipantAdmin(ModelView, model=Participant):
    name_plural = "Участники"
    icon = "fa-solid fa-person-falling-burst"
    column_list = [
        Participant.id,
        Participant.title,
        Participant.nomination,
        Participant.votes_count,
    ]
    column_labels = {
        Participant.id: "ID",
        Participant.title: "Название",
        Participant.nomination: "Номинация",
        Participant.votes_count: "Количество голосов",
    }
    form_columns = [Participant.title, Participant.nomination]
    column_searchable_list = [Participant.title]
    column_sortable_list = [Participant.votes_count]


class NominationAdmin(ModelView, model=Nomination):
    name_plural = "Номинации"
    icon = "fa-solid fa-graduation-cap"
    column_list = [
        Nomination.id,
        Nomination.title,
        Nomination.votable,
        Nomination.participants_count,
    ]
    column_labels = {
        Nomination.id: "ID",
        Nomination.title: "Название",
        Nomination.votable: "Голосование",
        Nomination.participants_count: "Количество участников",
    }
    form_include_pk = True
    form_columns = [Nomination.id, Nomination.title, Nomination.votable]


class VoteAdmin(ModelView, model=Vote):
    name_plural = "Голосование"
    icon = "fa-solid fa-square-poll-vertical"
    can_create = False
    can_edit = False
    column_list = [Vote.id, Vote.participant, Vote.user, Vote.time_created]
    column_labels = {
        Vote.id: "ID",
        Vote.participant: "Участник",
        Vote.user: "Пользователь",
        Vote.time_created: "Время голосования",
    }


class TransactionAdmin(ModelView, model=Transaction):
    name_plural = "Транзакции"
    icon = "fa-solid fa-money-bill-transfer"
    can_create = False
    can_edit = False
    can_delete = False
    column_list = [
        Transaction.id,
        Transaction.from_user,
        Transaction.to_user,
        Transaction.time_created,
        Transaction.achievement_added,
        Transaction.points_added,
    ]
    column_labels = {
        Transaction.id: "ID",
        Transaction.from_user: "От пользователя",
        Transaction.to_user: "Пользователю",
        Transaction.time_created: "Время",
        Transaction.achievement_added: "Достижение добавлено",
        Transaction.points_added: "Очков добавлено",
    }


model_views = [
    TicketAdmin,
    UserAdmin,
    AchievementAdmin,
    ReceivedAchievementAdmin,
    EventAdmin,
    ParticipantAdmin,
    NominationAdmin,
    VoteAdmin,
    TransactionAdmin,
]
