from pathlib import Path
from typing import List

from aiogram import types
from aiogram.types import Message, InputFile, InputMediaPhoto, FSInputFile
import json

from bot.handlers.cb_factories import ShowActivity
from bot.ui import strings

path_to_activities_folder = Path(__file__).parents[1] / 'activities'
activities_json = path_to_activities_folder / 'activities.json'


async def show(message: Message, id: int):
    if not id:
        id = 0
    with open(activities_json, mode='r') as f:
        activities = json.load(f)
    title = activities[id].get('title', '%title%')
    text = activities[id].get('text', '%text%')
    where = activities[id].get('where', '%where%')
    # image_path = activities[id]['image']
    f.close()
    kb = await keyboard(id, len(activities))
    message_text = f"<b>{title}</b>\n\n{text}\n\n<b>Где:</b> {where}"
    # image_file = FSInputFile(path=path_to_activities_folder.joinpath(image_path))
    # image = InputMediaPhoto(media=image_file)
    await message.edit_text(text=message_text, reply_markup=kb)


async def keyboard(id: int, total: int):
    navigation_buttons = []
    if id > 0:
        navigation_buttons.insert(0, types.InlineKeyboardButton(text="⏪",
                                                                callback_data=ShowActivity(id=0).pack()))
        navigation_buttons.insert(1, types.InlineKeyboardButton(text="◀️",
                                                                callback_data=ShowActivity(id=id-1).pack()))
    else:
        navigation_buttons.insert(0, types.InlineKeyboardButton(text="⠀",
                                                                callback_data='dummy'))
        navigation_buttons.insert(1, types.InlineKeyboardButton(text="⠀",
                                                                callback_data='dummy'))
    navigation_buttons.append(types.InlineKeyboardButton(text=f"{str(id+1)}/{str(total)}",
                                                         callback_data='dummy'))
    if id < total-1:
        navigation_buttons.append(types.InlineKeyboardButton(text="▶️",
                                                             callback_data=ShowActivity(id=id+1).pack()))
        navigation_buttons.append(types.InlineKeyboardButton(text="⏭️",
                                                             callback_data=ShowActivity(page=total).pack()))
    else:
        navigation_buttons.append(types.InlineKeyboardButton(text="⠀", callback_data='dummy'))
        navigation_buttons.append(types.InlineKeyboardButton(text="⠀", callback_data='dummy'))
    buttons = [navigation_buttons]
    buttons.append([types.InlineKeyboardButton(text=strings.buttons.back,
                                               callback_data='open_main_menu')])
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb
