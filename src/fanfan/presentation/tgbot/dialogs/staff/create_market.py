from aiogram.types import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.marketplace.create_market_by_participant import (
    CreateMarketByParticipant,
)
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.marketplace.api import open_market
from fanfan.presentation.tgbot.static import strings


@inject
async def create_market_by_participant_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
    create_market_by_participant: FromDishka[CreateMarketByParticipant],
) -> None:
    market = await create_market_by_participant(request_id=data)
    await message.reply(
        f"✅ Новый магазин <b>{market.name}</b> создан! "
        f"Не забудьте добавить его владельца в список управляющих."
    )
    await open_market(manager=dialog_manager, market_id=market.id)


create_market_window = Window(
    Const(
        "🛍️ С помощью этого инструмента можно быстро "
        "создать новый магазин на основе заявки с Cosplay2"
    ),
    Const(" "),
    Const("🌐 Найдите нужную заявку на Cosplay2 и пришлите её ID"),
    Const("Пример: URL-адрес каждой заявки на Cosplay2 имеет следующий вид:"),
    Const(
        "<blockquote>fanfan2025.cosplay2.ru/orgs/requests/request/<b>XXXXXX</b></blockquote>"
    ),
    Const("<b>XXXXXX</b> - ID заявки"),
    Const(" "),
    Const("""⚠️ Заявка должна иметь статус 'Принята', а БД бота - обновлена"""),
    TextInput(
        id="request_id_input",
        type_factory=int,
        on_success=create_market_by_participant_handler,
    ),
    SwitchTo(
        state=states.Staff.MAIN,
        id="org_main_window",
        text=Const(strings.buttons.back),
    ),
    disable_web_page_preview=True,
    state=states.Staff.CREATE_MARKET,
)
