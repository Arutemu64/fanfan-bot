from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.input.text import ManagedTextInput
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const

from src.bot.dialogs import states
from src.bot.dialogs.widgets import Title
from src.bot.ui import strings
from src.db import Database
from src.db.models import User


async def check_ticket(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    db: Database = dialog_manager.middleware_data["db"]
    current_user: User = dialog_manager.middleware_data["current_user"]
    ticket = await db.ticket.get(data)
    if ticket:
        if ticket.used_by is None:
            current_user.ticket = ticket
            current_user.role = ticket.role
            await db.session.commit()
            await message.answer(
                "✅ Билет успешно привязан! " "Теперь тебе доступны все функции бота!"
            )
            await dialog_manager.start(
                state=states.MAIN.MAIN,
            )
        else:
            await message.reply("⚠️ Этот билет уже был использован ранее!")
    else:
        await message.reply("⚠️ Билет не найден!")


link_ticket_window = Window(
    Title(strings.titles.ticket_linking),
    Const(
        "🎫 Чтобы привязать билет и получить доступ ко всем функциям бота "
        "пришли его номер сообщением 👇\n\n"
        "Пример номера билета: 66117533:43231829"
    ),
    Start(Const(strings.buttons.back), id="back", state=states.MAIN.MAIN),
    TextInput(id="ticket_id_input", type_factory=str, on_success=check_ticket),
    state=states.LINK_TICKET.ASK_TICKET_NUMBER,
)

dialog = Dialog(link_ticket_window)
