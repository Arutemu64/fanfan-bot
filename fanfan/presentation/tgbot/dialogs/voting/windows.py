import operator

from aiogram import F
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    Column,
    CurrentPage,
    FirstPage,
    LastPage,
    NextPage,
    PrevPage,
    Row,
    Select,
    StubScroll,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, Jinja

from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static.templates import voting_list
from fanfan.presentation.tgbot.ui import strings

from .constants import (
    DATA_SEARCH_QUERY,
    ID_NOMINATIONS_SCROLL,
    ID_VOTING_SCROLL,
)
from .getters import nominations_getter, participants_getter
from .handlers import (
    add_vote_handler,
    cancel_vote_handler,
    reset_search_handler,
    select_nomination_handler,
)

nominations_window = Window(
    Title(Const(strings.titles.voting)),
    Const("Для голосования доступны следующие номинации"),
    Column(
        Select(
            Format("{item[1]}"),
            id="nomination",
            item_id_getter=operator.itemgetter(0),
            items="nominations_list",
            type_factory=str,
            on_click=select_nomination_handler,
        ),
    ),
    StubScroll(ID_NOMINATIONS_SCROLL, pages="pages"),
    Row(
        FirstPage(scroll=ID_NOMINATIONS_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_NOMINATIONS_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_NOMINATIONS_SCROLL,
            text=Format(text="{current_page1}/{pages}"),
        ),
        NextPage(scroll=ID_NOMINATIONS_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_NOMINATIONS_SCROLL, text=Const("⏭️")),
        when=F["pages"] > 1,
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.VOTING.SELECT_NOMINATION,
    getter=nominations_getter,
)
voting_window = Window(
    Title(Format("🎖️ Номинация {nomination_title}")),
    Jinja(voting_list),
    Format(
        "🔍 Результаты поиска по запросу {dialog_data[data_search_query]}",
        when=F["dialog_data"][DATA_SEARCH_QUERY],
    ),
    Const("⌨️ Чтобы проголосовать, нажми на номер участника", when=~F["voted"]),
    Const(
        "🔍 <i>Для поиска отправь запрос сообщением</i>",
        when=~F["dialog_data"][DATA_SEARCH_QUERY],
    ),
    Button(
        text=Const("🔍❌ Сбросить поиск"),
        id="reset_search",
        on_click=reset_search_handler,
        when=F["dialog_data"][DATA_SEARCH_QUERY],
    ),
    Row(
        StubScroll(ID_VOTING_SCROLL, pages="pages"),
        FirstPage(scroll=ID_VOTING_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_VOTING_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_VOTING_SCROLL,
            text=Format(text="{current_page1}/{pages}"),
        ),
        NextPage(scroll=ID_VOTING_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_VOTING_SCROLL, text=Const("⏭️")),
        when=F["pages"] > 1,
    ),
    TextInput(
        id="vote_id_input",
        type_factory=str,
        on_success=add_vote_handler,
    ),
    Button(
        Const("🗑️ Отменить голос"),
        id="cancel_vote",
        when="voted",
        on_click=cancel_vote_handler,
    ),
    SwitchTo(
        text=Const(strings.buttons.back),
        state=states.VOTING.SELECT_NOMINATION,
        id="nominations",
    ),
    state=states.VOTING.VOTING,
    getter=participants_getter,
)
