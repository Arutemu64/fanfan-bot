import operator
from typing import Any

from aiogram import F
from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Column,
    CurrentPage,
    FirstPage,
    LastPage,
    NextPage,
    PrevPage,
    Row,
    Select,
    Start,
    StubScroll,
)
from aiogram_dialog.widgets.text import Const, Format, Jinja
from sqlalchemy import and_
from sqlalchemy.orm import undefer

from src.bot.dialogs import states
from src.bot.ui import strings
from src.config import conf
from src.db import Database
from src.db.models import Event, Nomination, Participant, User, Vote
from src.redis.global_settings import GlobalSettings

participants_per_page = conf.bot.participants_per_page
ID_VOTING_SCROLL = "voting_scroll"


async def show_nomination(
    callback: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str
):
    dialog_manager.dialog_data["nomination_id"] = item_id
    await dialog_manager.switch_to(states.VOTING.VOTING)
    return


async def get_nominations(dialog_manager: DialogManager, db: Database, **kwargs):
    nominations_list = []
    nominations = await db.nomination.get_many(Nomination.votable.is_(True))
    for nomination in nominations:
        nominations_list.append((nomination.title, nomination.id))
    return {"nominations_list": nominations_list}


async def get_participants(
    dialog_manager: DialogManager, db: Database, user: User, **kwargs
):
    nomination_id = dialog_manager.dialog_data["nomination_id"]
    nomination = await db.nomination.get(nomination_id)

    terms = and_(
        Participant.nomination_id == nomination.id,
        Participant.event.any(Event.hidden.isnot(True)),
    )
    pages = await db.participant.get_number_of_pages(participants_per_page, terms)
    current_page = await dialog_manager.find(ID_VOTING_SCROLL).get_page()
    participants = await db.participant.get_page(
        current_page,
        participants_per_page,
        query=terms,
        order_by=Participant.id,
        options=undefer(Participant.votes_count),
    )
    user_vote = await db.vote.get_by_where(
        and_(
            Vote.user_id == user.id,
            Vote.participant.has(Participant.nomination_id == nomination_id),
        )
    )
    if user_vote:
        dialog_manager.dialog_data["user_vote_id"] = user_vote.id
    else:
        dialog_manager.dialog_data["user_vote_id"] = None
    return {
        "pages": pages,
        "nomination_title": nomination.title,
        "participants": participants,
        "user_vote": user_vote,
    }


nominations = Window(
    Const("<b>📊 Голосование</b>"),
    Const(" "),
    Const("Для голосования доступны следующие номинации:"),
    Column(
        Select(
            Format("{item[0]}"),
            id="nomination",
            item_id_getter=operator.itemgetter(1),
            items="nominations_list",
            on_click=show_nomination,
        ),
    ),
    Start(text=Const(strings.buttons.back), id="mm", state=states.MAIN.MAIN),
    state=states.VOTING.NOMINATIONS,
    getter=get_nominations,
)

# fmt: off
participants_html = Jinja(  # noqa: E501
    "<b>Номинация {{nomination_title}}</b>"
    "\n"
    "В этой номинации представлены следующие участники:\n"
    "{% for participant in participants %}"
        "{% if user_vote.participant_id == participant.id %}"
            "<b>"
        "{% endif %}"
        "<b>{{participant.id}}.</b> {{participant.title}} "
        "{% if (participant.votes_count % 10 == 1) and (participant.votes_count % 100 != 11) %}"  # noqa: E501
            "[{{participant.votes_count}} голос]"
        "{% elif (2 <= participant.votes_count % 10 <= 4) and (participant.votes_count % 100 < 10 or participant.votes_count % 100 >= 20) %}"  # noqa: E501
            "[{{participant.votes_count}} голоса]"
        "{% else %}"
            "[{{participant.votes_count}} голосов]"
        "{% endif %}"
        "{% if user_vote.participant_id == participant.id %}"
            "</b> ✅"
        "{% endif %}"
        "\n\n"
    "{% endfor %}"
    "{% if not user_vote %}"
        "Чтобы проголосовать, просто отправь номер участника."
    "{% endif %}")
# fmt: on


async def vote(message: Message, message_input: MessageInput, manager: DialogManager):
    settings: GlobalSettings = manager.middleware_data["settings"]
    if not await settings.voting_enabled.get():
        await message.reply(strings.errors.voting_disabled)
        return
    if manager.dialog_data.get("user_vote_id"):
        await message.reply(strings.errors.already_voted)
        return
    if not message.text.isnumeric():
        await message.reply("Укажите номер выступающего!")
        return
    db: Database = manager.middleware_data["db"]
    participant = await db.participant.get_by_where(
        and_(
            Participant.id == int(message.text),
            Participant.nomination_id == manager.dialog_data["nomination_id"],
            Participant.event.any(Event.hidden.isnot(True)),
        )
    )
    if participant:
        await db.vote.new(message.from_user.id, participant.id)
        await db.session.commit()
    else:
        await message.reply("Неверно указан номер выступления")
        return


async def cancel_vote(callback: CallbackQuery, button: Button, manager: DialogManager):
    settings: GlobalSettings = manager.middleware_data["settings"]
    if not await settings.voting_enabled.get():
        await callback.answer(strings.errors.voting_disabled)
        return
    db: Database = manager.middleware_data["db"]
    user_vote = await db.vote.get(manager.dialog_data["user_vote_id"])
    await db.session.delete(user_vote)
    await db.session.commit()


async def reset_page(callback: CallbackQuery, button: Button, manager: DialogManager):
    await manager.find(ID_VOTING_SCROLL).set_page(0)
    return


voting = Window(
    participants_html,
    StubScroll(ID_VOTING_SCROLL, pages="pages"),
    Row(
        FirstPage(scroll=ID_VOTING_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_VOTING_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_VOTING_SCROLL, text=Format(text="{current_page1}/{pages}")
        ),
        NextPage(scroll=ID_VOTING_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_VOTING_SCROLL, text=Const("⏭️")),
        when=F["pages"] != 1,
    ),
    MessageInput(vote, content_types=[ContentType.TEXT]),
    Button(
        Const("Отменить голос"),
        id="cancel_vote",
        when="user_vote",
        on_click=cancel_vote,
    ),
    Back(text=Const(strings.buttons.back), on_click=reset_page),
    state=states.VOTING.VOTING,
    getter=get_participants,
)

dialog = Dialog(nominations, voting)
