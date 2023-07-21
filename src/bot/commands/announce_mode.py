from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram_dialog import DialogManager

from src.bot.dialogs import states
from src.bot.ui import strings
from src.db import Database
from src.db.models import Event

router = Router(name="announce_mode_router")

announcement_timestamp = 0


@router.message(Command("a"))
async def announce_mode(
    message: Message,
    db: Database,
    dialog_manager: DialogManager,
    command: CommandObject,
):
    current_event = Event()
    next_event = Event()
    args = command.args.split()
    current_arg = 0
    while current_arg < len(args):
        if args[current_arg].isnumeric():
            event = await db.event.get_by_where(Event.id == int(args[current_arg]))
            if event is None:
                await message.reply(strings.errors.wrong_command_usage)
                return
            if (current_event.id or current_event.text) is None:
                current_event = event
            elif (next_event.id or next_event.text) is None:
                next_event = event
            current_arg += 1
            continue
        elif args[current_arg] == "перерыв":
            if args[current_arg + 1].isnumeric():
                if (current_event.id or current_event.text) is None:
                    current_event.text = (
                        f"""перерыв на {str(args[current_arg + 1])} минут"""
                    )
                elif (next_event.id or next_event.text) is None:
                    next_event.text = (
                        f"""перерыв на {str(args[current_arg + 1])} минут"""
                    )
                current_arg += 2
                continue
            else:
                await message.reply("Неверно указано время перерыва!")
                return
        else:
            await message.reply(strings.errors.wrong_command_usage)
            return
    await dialog_manager.start(
        state=states.ANNOUNCE_MODE.PREVIEW,
        data={"current_event": current_event, "next_event": next_event},
    )
