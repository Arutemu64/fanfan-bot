import typing
from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import (
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
)
from aiogram_dialog.widgets.text import Const, Format
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.marketplace.get_markets_page import GetMarketsPage
from fanfan.core.dto.page import Pagination
from fanfan.core.dto.user import FullUserDTO
from fanfan.core.vo.market import MarketId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.utils import get_dialog_data_adapter
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.marketplace.data import (
    MarketDialogData,
)
from fanfan.presentation.tgbot.static import strings

ID_SELECT_MARKET = "select_market"
ID_MARKETS_SCROLL = "markets_scroll"

if typing.TYPE_CHECKING:
    from aiogram_dialog.widgets.common import ManagedScroll


@inject
async def list_markets_getter(
    dialog_manager: DialogManager,
    current_user: FullUserDTO,
    list_markets: FromDishka[GetMarketsPage],
    **kwargs,
):
    scroll: ManagedScroll = dialog_manager.find(ID_MARKETS_SCROLL)
    page = await list_markets(
        pagination=Pagination(
            limit=current_user.settings.items_per_page,
            offset=await scroll.get_page() * current_user.settings.items_per_page,
        )
    )
    pages = page.total // current_user.settings.items_per_page + bool(
        page.total % current_user.settings.items_per_page
    )
    return {
        "markets": page.items,
        "pages": pages or 1,
    }


async def on_market_selected(
    callback: CallbackQuery, widget: Any, manager: DialogManager, item_id: MarketId
):
    dialog_data_adapter = get_dialog_data_adapter(manager)
    dialog_data = dialog_data_adapter.load(MarketDialogData)
    dialog_data.market_id = item_id
    dialog_data_adapter.flush(dialog_data)
    await manager.switch_to(states.Marketplace.VIEW_MARKET)


list_markets_window = Window(
    Title(Const(strings.titles.marketplace)),
    Const(
        "<b>🛍️ Маркет</b> — это раздел, где собраны товары участников аллеи авторов и "
        "ярмарки. "
        "Здесь можно заранее ознакомиться с тем, что будет продаваться на фестивале: "
        "от уникальных сувениров до авторских изделий.\n\n"
        "📦 Каждый магазин — это витрина с описаниями, фото и ценами товаров.\n\n"
        "💬 Вы участник и хотите попасть в «Маркет»? Напишите куратору ярмарки."
    ),
    Column(
        Select(
            Format("{item.name}"),
            id=ID_SELECT_MARKET,
            item_id_getter=lambda item: item.id,
            items="markets",
            type_factory=lambda value: MarketId(int(value)),
            on_click=on_market_selected,
        ),
    ),
    Row(
        StubScroll(ID_MARKETS_SCROLL, pages="pages"),
        FirstPage(scroll=ID_MARKETS_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_MARKETS_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_MARKETS_SCROLL,
            text=Format(text="{current_page1}/{pages}"),
        ),
        NextPage(scroll=ID_MARKETS_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_MARKETS_SCROLL, text=Const("⏭️")),
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.Marketplace.LIST_MARKETS,
    getter=list_markets_getter,
)
