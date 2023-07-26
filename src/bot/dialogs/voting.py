import operator
from typing import Any

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Button, Column, Select, Start
from aiogram_dialog.widgets.text import Const, Format, Jinja, Text
from sqlalchemy import and_

from src.bot.dialogs import states
from src.bot.ui import strings
from src.db import Database
from src.db.models import Nomination, Participant, Vote


async def show_nomination(
    callback: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str
):
    dialog_manager.dialog_data["nomination_id"] = item_id
    await dialog_manager.switch_to(states.VOTING.VOTING)
    return


async def get_nominations(dialog_manager: DialogManager, db: Database, **kwargs):
    nominations_list = []
    nominations = await db.nomination.get_many(True)
    for nomination in nominations:
        if nomination.votable:
            nominations_list.append((nomination.title, nomination.id))
    return {"nominations_list": nominations_list}


async def get_participants(dialog_manager: DialogManager, db: Database, **kwargs):
    nomination_id = dialog_manager.dialog_data["nomination_id"]
    nomination = await db.nomination.get_by_where(Nomination.id == nomination_id)
    participants = nomination.participants
    user_vote: Vote = await db.vote.get_by_where(
        and_(
            Vote.tg_id == dialog_manager.event.from_user.id,
            Vote.participant.has(Participant.nomination_id == nomination_id),
        )
    )
    if user_vote:
        dialog_manager.dialog_data["user_vote_id"] = user_vote.id
    else:
        dialog_manager.dialog_data["user_vote_id"] = None
    return {
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
participants_html = Jinja(
    "<b>Номинация {{nomination_title}}</b>"
    "\n"
    "В этой номинации представлены следующие участники:\n"
    "{% for participant in participants %}"
    "{% if user_vote.participant_id == participant.id %}"
    "<b>{{participant.id}}. {{participant.title}}</b> [голосов: {{participant.votes|length}}] ✅\n"
    "{% else %}"
    "<b>{{participant.id}}.</b> {{participant.title}} [голосов: {{participant.votes|length}}]\n"
    "{% endif %}"
    "{% endfor %}"
    "Чтобы проголосовать, просто отправь номер участника.")


# fmt: on


async def vote(message: Message, message_input: MessageInput, manager: DialogManager):
    db: Database = manager.middleware_data["db"]
    settings = await db.settings.get_by_where(True)
    if not settings.voting_enabled:
        await message.reply(strings.errors.voting_disabled)
        return
    if manager.dialog_data.get("user_vote_id"):
        await message.reply(strings.errors.already_voted)
        return
    if not message.text.isnumeric():
        await message.reply("Укажите номер выступающего!")
        return
    participant: Participant = await db.participant.get(int(message.text))
    if participant:
        await db.vote.new(message.from_user.id, participant.id)
        await db.session.commit()
    else:
        await message.reply(strings.errors.performance_doesnt_exist)
        return


async def cancel_vote(callback: CallbackQuery, button: Button, manager: DialogManager):
    db: Database = manager.middleware_data["db"]
    settings = await db.settings.get_by_where(True)
    if not settings.voting_enabled:
        await callback.answer(strings.errors.voting_disabled)
        return
    user_vote: Vote = await db.vote.get(manager.dialog_data["user_vote_id"])
    await db.session.delete(user_vote)
    await db.session.commit()


voting = Window(
    participants_html,
    MessageInput(vote, content_types=[ContentType.TEXT]),
    Button(
        Const("Отменить голос"),
        id="cancel_vote",
        when="user_vote",
        on_click=cancel_vote,
    ),
    Back(text=Const(strings.buttons.back)),
    state=states.VOTING.VOTING,
    getter=get_participants,
)

dialog = Dialog(nominations, voting)
