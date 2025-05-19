import typing

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Button,
    Group,
    SwitchTo,
)
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Case, Const, Jinja, Multi

from fanfan.application.marketplace.read_market import ReadMarket
from fanfan.application.marketplace.update_market import UpdateMarket
from fanfan.core.vo.market import MarketId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.marketplace.common import DATA_SELECTED_MARKET_ID
from fanfan.presentation.tgbot.dialogs.marketplace.market.common import market_getter
from fanfan.presentation.tgbot.static import strings

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer


async def change_market_visibility(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    container: AsyncContainer = manager.middleware_data["container"]
    market_id = MarketId(manager.dialog_data[DATA_SELECTED_MARKET_ID])

    get_market: ReadMarket = await container.get(ReadMarket)
    update_market: UpdateMarket = await container.get(UpdateMarket)

    market = await get_market(market_id=market_id)
    await update_market.update_market_visibility(
        market_id=market_id, is_visible=not market.is_visible
    )
    market = await get_market(market_id=market_id)

    if market.is_visible:
        await callback.answer("✅ Теперь магазин видим для остальных")
    else:
        await callback.answer("❎ Магазин скрыт")


view_market_window = Window(
    DynamicMedia(
        selector="market_image",
        when="market_image",
    ),
    Title(Jinja("🛍️ {{ market_name }}")),
    Multi(Jinja("{{ market_description }}"), Const(" "), when="market_description"),
    Multi(
        Const("<i>Вы управляете этим магазином</i>"),
        Jinja("<i>ID магазина: {{ market_id }}</i>"),
        Jinja(
            "<i>Управляющие: "
            "{% for m in market_managers %}"
            "@{{m.username}}{% if not loop.last %}, {% endif %}"
            "{% endfor %}</i>"
        ),
        when="market_is_manager",
    ),
    SwitchTo(
        Const("📦 Смотреть каталог"),
        state=states.Marketplace.LIST_PRODUCTS,
        id="open_catalog",
    ),
    Group(
        Button(
            Case(
                texts={
                    True: Const("👁️ Видимость магазина для всех: ✅"),
                    False: Const("👁️ Видимость магазина для всех: ❎"),
                },
                selector="market_is_visible",
            ),
            on_click=change_market_visibility,
            id="toggle_market_visibility",
        ),
        SwitchTo(
            Const("✏️ Изменить название"),
            state=states.Marketplace.EDIT_MARKET_NAME,
            id="edit_market_name",
        ),
        SwitchTo(
            Const("💬 Изменить описание"),
            state=states.Marketplace.EDIT_MARKET_DESCRIPTION,
            id="edit_market_description",
        ),
        SwitchTo(
            Const("🖼️ Изменить изображение"),
            state=states.Marketplace.EDIT_MARKET_IMAGE,
            id="edit_market_picture",
        ),
        SwitchTo(
            Const("💼 Добавить нового управляющего"),
            state=states.Marketplace.ADD_MANAGER,
            id="add_manager",
        ),
        when="market_is_manager",
    ),
    SwitchTo(
        Const(strings.buttons.back), state=states.Marketplace.LIST_MARKETS, id="back"
    ),
    getter=market_getter,
    state=states.Marketplace.VIEW_MARKET,
)
