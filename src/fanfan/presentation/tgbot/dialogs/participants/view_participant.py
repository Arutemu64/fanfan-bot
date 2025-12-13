from dataclasses import dataclass

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.adapters.api.cosplay2.config import Cosplay2Config
from fanfan.application.marketplace.create_market_by_participant import (
    CreateMarketByParticipant,
)
from fanfan.application.participants.get_participant_by_id import GetParticipantById
from fanfan.core.constants.permissions import Permissions
from fanfan.core.dto.user import FullUserDTO
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.utils import get_dialog_data_adapter
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.marketplace.api import open_market
from fanfan.presentation.tgbot.dialogs.participants.data import (
    ParticipantsViewerData,
)
from fanfan.presentation.tgbot.dialogs.participants.utils import parse_value
from fanfan.presentation.tgbot.middlewares.dialog_data_adapter import DialogDataAdapter
from fanfan.presentation.tgbot.static import strings
from fanfan.presentation.tgbot.templates import view_participant


@dataclass(slots=True, kw_only=True)
class FormattedValue:
    title: str
    value: str | None


@inject
async def view_participant_getter(
    dialog_manager: DialogManager,
    dialog_data_adapter: DialogDataAdapter,
    current_user: FullUserDTO,
    get_participant: FromDishka[GetParticipantById],
    cosplay2_config: FromDishka[Cosplay2Config],
    **kwargs,
) -> dict:
    dialog_data = dialog_data_adapter.load(ParticipantsViewerData)
    participant = await get_participant(dialog_data.participant_id)
    formatted_values = [
        FormattedValue(
            title=value.title,
            value=parse_value(
                value, participant_id=participant.id, event_id=cosplay2_config.event_id
            ),
        )
        for value in participant.values
    ]
    can_create_market = current_user.check_permission(Permissions.CAN_CREATE_MARKET)
    return {
        "title": participant.title,
        "values": formatted_values,
        # Permissions
        "can_create_market": can_create_market,
    }


@inject
async def create_market(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    create_market_by_participant: FromDishka[CreateMarketByParticipant],
) -> None:
    dialog_data_adapter = get_dialog_data_adapter(manager)
    dialog_data = dialog_data_adapter.load(ParticipantsViewerData)
    market = await create_market_by_participant(
        participant_id=dialog_data.participant_id
    )
    await callback.answer(
        f"✅ Новый магазин <b>{market.name}</b> создан! "
        f"Не забудьте добавить его владельца в список управляющих."
    )
    await open_market(manager=manager, market_id=market.id)


view_participant_window = Window(
    Title(Const("📃 Информация об участнике")),
    Jinja(view_participant),
    Button(
        text=Const("🏪 Создать магазин"),
        id="create_market",
        on_click=create_market,
        when="can_create_market",
    ),
    SwitchTo(
        text=Const(strings.buttons.back),
        state=states.Participants.LIST_PARTICIPANTS,
        id="participants",
    ),
    disable_web_page_preview=True,
    getter=view_participant_getter,
    state=states.Participants.VIEW_PARTICIPANT,
)
