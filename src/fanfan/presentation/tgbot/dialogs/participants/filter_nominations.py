import operator
from typing import TYPE_CHECKING

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Button,
    ManagedMultiselect,
    Multiselect,
    ScrollingGroup,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Jinja
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.nominations.list_nominations import (
    ListNominations,
    ListNominationsDTO,
)
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.handlers.inline_query import (
    INLINE_DATA_SELECTED_NOMINATION_IDS,
)
from fanfan.presentation.tgbot.static import strings

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

ID_NOMINATIONS_FILTER = "nominations_filter"


@inject
async def list_participants_getter(
    dialog_manager: DialogManager,
    list_nominations: FromDishka[ListNominations],
    **kwargs,
) -> dict:
    page = await list_nominations(ListNominationsDTO())
    nominations_filter: ManagedMultiselect = dialog_manager.find(ID_NOMINATIONS_FILTER)
    return {"nominations": page.items, "checked": nominations_filter.get_checked()}


async def reset_checked(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    nominations_filter: ManagedMultiselect = manager.find(ID_NOMINATIONS_FILTER)
    state: FSMContext = manager.middleware_data["state"]
    await nominations_filter.reset_checked()
    await state.update_data({INLINE_DATA_SELECTED_NOMINATION_IDS: None})


async def on_state_changed(
    event: CallbackQuery,
    widget: ManagedMultiselect,
    dialog_manager: DialogManager,
    item_id: str,
):
    # Sync selected nomination ids to FSM to work with inline
    state: FSMContext = dialog_manager.middleware_data["state"]
    nomination_ids = widget.get_checked()
    await state.update_data({INLINE_DATA_SELECTED_NOMINATION_IDS: nomination_ids})


filter_nominations_window = Window(
    Title(Const("Фильтр номинаций")),
    Const(
        "По умолчанию отображаются все номинации. "
        "Отметьте нужные номинации, по которым хотите вести поиск."
    ),
    ScrollingGroup(
        Multiselect(
            Jinja("✓ {{item.title}}"),
            Jinja("{{item.title}}"),
            id=ID_NOMINATIONS_FILTER,
            item_id_getter=operator.attrgetter("id"),
            items="nominations",
            on_state_changed=on_state_changed,
            type_factory=int,
        ),
        id="group",
        height=5,
        width=1,
    ),
    Button(
        text=Const("❌ Сбросить отметки"),
        id="reset_checked",
        on_click=reset_checked,
        when="checked",
    ),
    SwitchTo(
        text=Const(strings.buttons.back),
        state=states.Participants.LIST_PARTICIPANTS,
        id="participants",
    ),
    getter=list_participants_getter,
    state=states.Participants.FILTER_NOMINATIONS,
)
