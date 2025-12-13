from aiogram.types import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Cancel,
    CurrentPage,
    FirstPage,
    LastPage,
    ManagedMultiselect,
    NextPage,
    PrevPage,
    Row,
    StubScroll,
    SwitchInlineQueryCurrentChat,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, Jinja
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.participants.list_participants import (
    ListParticipants,
    ListParticipantsDTO,
)
from fanfan.core.dto.page import Pagination
from fanfan.core.dto.user import FullUserDTO
from fanfan.core.vo.nomination import NominationId
from fanfan.core.vo.participant import ParticipantId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.utils import get_dialog_data_adapter
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.participants.data import (
    ParticipantsViewerData,
)
from fanfan.presentation.tgbot.dialogs.participants.filter_nominations import (
    ID_NOMINATIONS_FILTER,
)
from fanfan.presentation.tgbot.static import strings
from fanfan.presentation.tgbot.templates import participants_list

ID_PARTICIPANTS_SCROLL = "participants_scroll"


@inject
async def list_participants_getter(
    dialog_manager: DialogManager,
    current_user: FullUserDTO,
    list_participants: FromDishka[ListParticipants],
    **kwargs,
) -> dict:
    nominations_filter: ManagedMultiselect = dialog_manager.find(ID_NOMINATIONS_FILTER)
    nomination_ids = [NominationId(int(n)) for n in nominations_filter.get_checked()]
    page = await list_participants(
        data=ListParticipantsDTO(
            pagination=Pagination(
                limit=current_user.settings.items_per_page,
                offset=await dialog_manager.find(ID_PARTICIPANTS_SCROLL).get_page()
                * current_user.settings.items_per_page,
            ),
            nomination_ids=nomination_ids,
        )
    )
    pages = page.total // current_user.settings.items_per_page + bool(
        page.total % current_user.settings.items_per_page
    )
    return {
        "participants": page.items,
        "pages": pages or 1,
    }


@inject
async def list_participants_input_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    dialog_data_adapter = get_dialog_data_adapter(dialog_manager)
    dialog_data = dialog_data_adapter.load(ParticipantsViewerData)
    if "/" in data and data.replace("/", "").isnumeric():
        dialog_data.participant_id = ParticipantId(int(data.replace("/", "")))
        dialog_data_adapter.flush(dialog_data)
        await dialog_manager.switch_to(states.Participants.VIEW_PARTICIPANT)


list_participants_window = Window(
    Title(Const(strings.titles.participants)),
    Jinja(participants_list),
    StubScroll(ID_PARTICIPANTS_SCROLL, pages="pages"),
    Row(
        FirstPage(scroll=ID_PARTICIPANTS_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_PARTICIPANTS_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_PARTICIPANTS_SCROLL,
            text=Format(text="{current_page1}/{pages}"),
        ),
        NextPage(scroll=ID_PARTICIPANTS_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_PARTICIPANTS_SCROLL, text=Const("⏭️")),
    ),
    Row(
        SwitchTo(
            text=Const("🌪️ Фильтр"),
            id="filter_nominations",
            state=states.Participants.FILTER_NOMINATIONS,
        ),
        SwitchInlineQueryCurrentChat(
            text=Const(strings.buttons.search),
            switch_inline_query_current_chat=Const(""),
        ),
    ),
    Cancel(Const(strings.buttons.back)),
    TextInput(
        id="participant_id_input",
        type_factory=str,
        on_success=list_participants_input_handler,
    ),
    getter=list_participants_getter,
    state=states.Participants.LIST_PARTICIPANTS,
)
