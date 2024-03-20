from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.input.text import ManagedTextInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const

from fanfan.application.exceptions import ServiceError
from fanfan.application.holder import AppHolder
from fanfan.presentation.tgbot.dialogs import states
from fanfan.presentation.tgbot.dialogs.widgets import Title
from fanfan.presentation.tgbot.ui import strings


async def link_ticket_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    app: AppHolder = dialog_manager.middleware_data["app"]
    try:
        user_id = dialog_manager.event.from_user.id
        await app.tickets.link_ticket(ticket_id=data, user_id=user_id)
        dialog_manager.middleware_data["user"] = await app.users.get_user_by_id(user_id)
    except ServiceError as e:
        await message.reply(e.message)
        return
    await message.answer(
        "✅ Билет успешно привязан! Теперь тебе доступны все функции бота!"
    )
    await dialog_manager.start(states.MAIN.HOME, mode=StartMode.RESET_STACK)


link_ticket_window = Window(
    Title(Const(strings.titles.ticket_linking)),
    Const(
        "🎫 Чтобы привязать билет и получить доступ ко всем функциям бота "
        "пришли его номер сообщением 👇\n\n"
        "Пример номера билета: 66117533:43231829"
    ),
    SwitchTo(Const(strings.buttons.back), id="back", state=states.MAIN.HOME),
    TextInput(id="ticket_id_input", type_factory=str, on_success=link_ticket_handler),
    state=states.MAIN.LINK_TICKET,
)
