import operator
from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Back, Select, Start
from aiogram_dialog.widgets.text import Const, Format
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Nomination, Participant, Vote
from bot.dialogs import states
from bot.ui.strings import buttons


async def show_nomination(
    callback: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str
):
    dialog_manager.dialog_data["nomination_id"] = item_id
    await dialog_manager.switch_to(states.VOTING.VOTING)
    return


async def get_nominations(
    dialog_manager: DialogManager, session: AsyncSession, **kwargs
):
    nominations_list = []
    nominations = await Nomination.get_many(session, True)
    for nomination in nominations:
        nominations_list.append((nomination.title, nomination.id))
    return {"nominations_list": nominations_list}


async def get_participants(
    dialog_manager: DialogManager, session: AsyncSession, **kwargs
):
    nomination_id = dialog_manager.dialog_data["nomination_id"]
    nomination = await Nomination.get_one(session, Nomination.id == nomination_id)
    user_vote = await Vote.get_one(
        session,
        and_(
            Vote.tg_id == dialog_manager.event.from_user.id,
            Vote.participant.has(Participant.nomination_id == nomination_id),
        ),
    )
    participants_list = ""
    for participant in nomination.participants:
        entry = f"<b>{str(participant.id)}.</b> {participant.title} [голосов: {len(participant.votes)}]"
        if user_vote is not None:
            if user_vote.participant_id == participant.id:
                entry = f"<b>{entry} ✅</b>"
        if participant != nomination.participants[-1]:
            entry = entry + "\n"
        participants_list = participants_list + entry
    return {
        "nomination_title": nomination.title,
        "participants_list": participants_list,
    }


nominations = Window(
    Const("<b>📊 Голосование</b>"),
    Const(" "),
    Const("Для голосования доступны следующие номинации:"),
    Select(
        Format("{item[0]}"),
        id="nomination",
        item_id_getter=operator.itemgetter(1),
        items="nominations_list",
        on_click=show_nomination,
    ),
    Start(text=Const(buttons.back), id="mm", state=states.MAIN.MAIN),
    state=states.VOTING.NOMINATIONS,
    getter=get_nominations,
)

voting = Window(
    Format("<b>Номинация {nomination_title}</b>"),
    Const(" "),
    Const("В этой номинации представлены следующие участники:"),
    Format("{participants_list}"),
    Const(" "),
    Const("Чтобы проголосовать, используй команду <code>/vote номер_участника</code>"),
    Const("Отменить голос можно командой <code>/unvote номер_участника</code>"),
    Back(text=Const(buttons.back)),
    state=states.VOTING.VOTING,
    getter=get_participants,
)

dialog = Dialog(nominations, voting)
