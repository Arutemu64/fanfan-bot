from typing import List

from sqladmin import ModelView

from fanfan.infrastructure.db.models import (
    Achievement,
    Activity,
    Event,
    Nomination,
    Participant,
    Quote,
    ReceivedAchievement,
    Ticket,
    Transaction,
    User,
    Vote,
)


class TicketAdmin(ModelView, model=Ticket):
    name_plural = "Билеты"
    icon = "fa-solid fa-ticket"
    column_labels = {
        Ticket.id: "Номер билета",
        Ticket.role: "Роль",
        Ticket.used_by: "Использовал",
        Ticket.issued_by: "Выпустил",
        Ticket.created_on: "Время создания",
        Ticket.updated_on: "Время изменения",
    }
    column_list = [Ticket.id, Ticket.role, Ticket.used_by, Ticket.issued_by]
    column_details_exclude_list = [Ticket.used_by_id, Ticket.issued_by_id]
    form_include_pk = True
    form_columns = [Ticket.id, Ticket.role]
    column_searchable_list = [Ticket.id, Ticket.role]


class UserAdmin(ModelView, model=User):
    name_plural = "Пользователи"
    icon = "fa-solid fa-users"
    can_create = False
    column_labels = {
        User.id: "Telegram ID",
        User.username: "Имя пользователя",
        User.role: "Роль",
        User.achievements_count: "Достижений получено",
        User.points: "Очков",
        User.ticket: "Билет пользователя",
        User.items_per_page: "Элементов на странице",
        User.receive_all_announcements: "Получает глобальные уведомления",
        User.created_on: "Время создания",
        User.updated_on: "Время изменения",
    }
    column_list = [
        User.id,
        User.username,
        User.role,
        User.achievements_count,
        User.points,
    ]
    column_details_exclude_list = [User.received_achievements]
    column_searchable_list = [User.username, User.role]
    column_sortable_list = [User.achievements_count, User.points]


class AchievementAdmin(ModelView, model=Achievement):
    name_plural = "Достижения"
    icon = "fa-solid fa-trophy"
    column_labels = {
        Achievement.id: "ID",
        Achievement.title: "Название",
        Achievement.description: "Описание",
        Achievement.created_on: "Время создания",
        Achievement.updated_on: "Время изменения",
    }
    column_list = [Achievement.id, Achievement.title, Achievement.description]
    column_details_exclude_list = [Achievement.user_received]
    form_columns = [Achievement.id, Achievement.title, Achievement.description]
    form_include_pk = True


class ReceivedAchievementAdmin(ModelView, model=ReceivedAchievement):
    name_plural = "Полученные достижения"
    icon = "fa-solid fa-star"
    column_labels = {
        ReceivedAchievement.user: "Пользователь",
        ReceivedAchievement.achievement: "Достижение",
        ReceivedAchievement.created_on: "Время создания",
        ReceivedAchievement.updated_on: "Время изменения",
    }
    column_list = [
        ReceivedAchievement.user,
        ReceivedAchievement.achievement,
        ReceivedAchievement.created_on,
    ]
    can_create = False
    can_edit = False


class EventAdmin(ModelView, model=Event):
    name_plural = "Расписание"
    icon = "fa-solid fa-calendar-days"
    column_labels = {
        Event.id: "ID",
        Event.position: "Позиция",
        Event.real_position: "Позиция (с учётом пропусков)",
        Event.title: "Название",
        Event.current: "Текущее",
        Event.skip: "Пропущено",
        Event.nomination: "Номинация",
        Event.participant: "Участник",
        Event.created_on: "Время создания",
        Event.updated_on: "Время изменения",
    }
    column_list = [
        Event.id,
        Event.position,
        Event.real_position,
        Event.title,
        Event.current,
        Event.skip,
    ]
    form_columns = {
        Event.position,
        Event.title,
        Event.skip,
        Event.participant,
    }
    column_sortable_list = [Event.real_position]
    column_details_exclude_list = [Event.user_subscription, Event.participant_id]


class ParticipantAdmin(ModelView, model=Participant):
    name_plural = "Участники"
    icon = "fa-solid fa-person-falling-burst"
    column_labels = {
        Participant.id: "ID",
        Participant.title: "Название",
        Participant.nomination: "Номинация",
        Participant.votes_count: "Количество голосов",
        Participant.created_on: "Время создания",
        Participant.updated_on: "Время изменения",
    }
    column_list = [
        Participant.id,
        Participant.title,
        Participant.nomination,
        Participant.votes_count,
    ]
    form_columns = [Participant.title, Participant.nomination]
    column_searchable_list = [Participant.title]
    column_sortable_list = [Participant.votes_count]
    column_details_exclude_list = [Participant.user_vote, Participant.nomination]


class NominationAdmin(ModelView, model=Nomination):
    name_plural = "Номинации"
    icon = "fa-solid fa-graduation-cap"
    column_labels = {
        Nomination.id: "ID",
        Nomination.title: "Название",
        Nomination.votable: "Голосование",
        Nomination.created_on: "Время создания",
        Nomination.updated_on: "Время изменения",
    }
    column_list = [
        Nomination.id,
        Nomination.title,
        Nomination.votable,
    ]
    form_include_pk = True
    form_columns = [Nomination.id, Nomination.title, Nomination.votable]


class VoteAdmin(ModelView, model=Vote):
    name_plural = "Голоса"
    icon = "fa-solid fa-square-poll-vertical"
    column_labels = {
        Vote.id: "ID",
        Vote.participant: "Участник",
        Vote.user: "Пользователь",
        Vote.created_on: "Время создания",
        Vote.updated_on: "Время изменения",
    }
    can_create = False
    can_edit = False
    column_list = [Vote.id, Vote.participant, Vote.user, Vote.created_on]
    column_details_exclude_list = [Vote.participant_id, Vote.user_id]


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
        Transaction.created_on,
        Transaction.achievement_added,
        Transaction.points_added,
    ]
    column_labels = {
        Transaction.id: "ID",
        Transaction.from_user: "От пользователя",
        Transaction.to_user: "Пользователю",
        Transaction.created_on: "Время",
        Transaction.achievement_added: "Достижение добавлено",
        Transaction.points_added: "Очков добавлено",
    }


class ActivityAdmin(ModelView, model=Activity):
    name_plural = "Активности"
    icon = "fa-solid fa-person-snowboarding"
    column_list = [
        Activity.id,
        Activity.title,
    ]
    column_labels = {
        Activity.id: "ID",
        Activity.title: "Название",
        Activity.description: "Описание",
        Activity.subtext: "Подтекст",
        Activity.image: "Изображение",
    }
    form_columns = [
        Activity.title,
        Activity.description,
        Activity.subtext,
        Activity.image,
    ]


class QuoteAdmin(ModelView, model=Quote):
    name = "Подписи"
    icon = "fa-solid fa-pen"
    column_list = [
        Quote.id,
        Quote.text,
    ]
    column_labels = {
        Quote.id: "ID",
        Quote.text: "Название",
        Activity.description: "Описание",
        Activity.subtext: "Подтекст",
        Activity.image: "Изображение",
    }
    form_columns = [
        Quote.text,
    ]


model_views: List[ModelView] = [
    TicketAdmin,
    UserAdmin,
    AchievementAdmin,
    ReceivedAchievementAdmin,
    EventAdmin,
    ParticipantAdmin,
    NominationAdmin,
    VoteAdmin,
    TransactionAdmin,
    ActivityAdmin,
    QuoteAdmin,
]
