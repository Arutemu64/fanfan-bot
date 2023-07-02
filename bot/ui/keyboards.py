from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from bot.config import conf
from bot.db.models import Settings
from bot.ui import strings


def main_menu_kb(user_group):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text=strings.buttons.changelog_channel, url="https://t.me/fanfan_bot_dev_notes"))
    builder.row(types.InlineKeyboardButton(text=strings.buttons.notifications_channel, url=conf.channel_link))
    builder.row(types.InlineKeyboardButton(text=strings.buttons.show_schedule, callback_data="update_schedule"))
    builder.row(types.InlineKeyboardButton(text=strings.buttons.voting, callback_data="open_nominations_menu"))
    helper_button = types.InlineKeyboardButton(text=strings.buttons.helper_menu, callback_data="open_helper_menu")
    org_button = types.InlineKeyboardButton(text=strings.buttons.org_menu, callback_data="open_org_menu")
    match user_group:
        case "helper":
            builder.row(helper_button)
        case "org":
            builder.row(helper_button, org_button)
    return builder.as_markup()


def nominations_menu_kb(nominations):
    builder = InlineKeyboardBuilder()
    for nomination in nominations:
        builder.row(types.InlineKeyboardButton(text=nomination.name,
                                               callback_data='nomination ' + str(nomination.id)))
    builder.row(types.InlineKeyboardButton(text=strings.buttons.back,
                                           callback_data='open_main_menu'))
    return builder.as_markup()


def voting_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text=strings.buttons.back,
                                           callback_data='open_nominations_menu'))
    return builder.as_markup()


def helper_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text=strings.buttons.announce_mode,
                                           callback_data='announce_mode'))
    builder.row(types.InlineKeyboardButton(text=strings.buttons.back,
                                           callback_data='open_main_menu'))
    return builder.as_markup()


def org_menu_kb(settings: Settings):
    builder = InlineKeyboardBuilder()
    if settings.voting_enabled:
        builder.row(types.InlineKeyboardButton(text=strings.buttons.disable_voting,
                                               callback_data='switch_voting'))
    else:
        builder.row(types.InlineKeyboardButton(text=strings.buttons.enable_voting,
                                               callback_data='switch_voting'))
    builder.row(types.InlineKeyboardButton(text=strings.buttons.back,
                                           callback_data='open_main_menu'))
    return builder.as_markup()


def send_kb(current_event_id=None, next_event_id=None):
    builder = InlineKeyboardBuilder()
    callback_data = 'send_announcement'
    if current_event_id:
        callback_data = f"{callback_data} {str(current_event_id)}"
    else:
        callback_data = f"{callback_data} -1"
    if next_event_id:
        callback_data = f"{callback_data} {str(next_event_id)}"
    builder.row(types.InlineKeyboardButton(text=strings.buttons.send,
                                           callback_data=callback_data))
    builder.row(types.InlineKeyboardButton(text=strings.buttons.delete,
                                           callback_data='delete_message'))
    return builder.as_markup()


def announce_mode_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text=strings.buttons.next))
    builder.row(types.KeyboardButton(text=strings.buttons.show_schedule))
    builder.row(types.KeyboardButton(text=strings.buttons.back))
    return builder.as_markup(resize_keyboard=True)


def schedule_menu_kb(page, total_pages: int, show_back_button: bool = False):
    navigation_buttons = []
    if page > 0:
        navigation_buttons.insert(0, types.InlineKeyboardButton(text="⏪",
                                                                callback_data='open_schedule_page 0'))
        navigation_buttons.insert(1, types.InlineKeyboardButton(text="◀️",
                                                                callback_data='open_schedule_page ' + str(page - 1)))
    else:
        navigation_buttons.insert(0, types.InlineKeyboardButton(text="⠀", callback_data='dummy'))
        navigation_buttons.insert(1, types.InlineKeyboardButton(text="⠀", callback_data='dummy'))
    navigation_buttons.append(types.InlineKeyboardButton(text="🔃",
                                                         callback_data='open_schedule_page'))
    if page < total_pages:
        navigation_buttons.append(types.InlineKeyboardButton(text="▶️",
                                                             callback_data='open_schedule_page ' + str(page + 1)))
        navigation_buttons.append(types.InlineKeyboardButton(text="⏭️",
                                                             callback_data='open_schedule_page ' + str(total_pages)))
    else:
        navigation_buttons.append(types.InlineKeyboardButton(text="⠀", callback_data='dummy'))
        navigation_buttons.append(types.InlineKeyboardButton(text="⠀", callback_data='dummy'))
    buttons = [navigation_buttons]
    if show_back_button:
        buttons.append([types.InlineKeyboardButton(text=strings.buttons.back,
                                                   callback_data='open_main_menu')])
    kb = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return kb
