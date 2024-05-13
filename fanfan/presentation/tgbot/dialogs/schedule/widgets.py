from aiogram import F
from aiogram_dialog.widgets.kbd import (
    Button,
    FirstPage,
    Group,
    LastPage,
    NextPage,
    PrevPage,
    Row,
    StubScroll,
)
from aiogram_dialog.widgets.text import Const, Format, Multi

from .constants import (
    DATA_SEARCH_QUERY,
    ID_SCHEDULE_SCROLL,
)
from .handlers import (
    reset_search_handler,
    update_schedule_handler,
)

SCHEDULE_SCROLL = Group(
    Row(
        StubScroll(ID_SCHEDULE_SCROLL, pages="pages"),
        FirstPage(scroll=ID_SCHEDULE_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_SCHEDULE_SCROLL, text=Const("◀️")),
        Button(
            text=Format(text="{page_number} 🔄️"),
            id="update_schedule",
            on_click=update_schedule_handler,
        ),
        NextPage(scroll=ID_SCHEDULE_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_SCHEDULE_SCROLL, text=Format("⏭️")),
    )
)

SEARCH_INDICATOR = Multi(
    Const(
        "<i>🔍 Отправь текст/номер выступления</i>",
        when=~F["dialog_data"][DATA_SEARCH_QUERY],
    ),
    Format(
        "<blockquote><b>🔍 {dialog_data[data_search_query]}</b></blockquote>",
        when=F["dialog_data"][DATA_SEARCH_QUERY],
    ),
)

RESET_SEARCH_BUTTON = Button(
    text=Const("❌ Сбросить поиск"),
    id="reset_search",
    on_click=reset_search_handler,
    when=F["dialog_data"][DATA_SEARCH_QUERY],
)
