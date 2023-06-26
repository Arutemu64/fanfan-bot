from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types

from bot.ui import strings

from bot.db.models import Settings

from bot.config import conf


def main_menu_kb(user_group, notifications_enabled):
    builder = InlineKeyboardBuilder()
    # if notifications_enabled:
    #     builder.row(types.InlineKeyboardButton(text=strings.disable_notifications_button,
    #                                            callback_data="switch_notifications"))
    # else:
    #     builder.row(types.InlineKeyboardButton(text=strings.enable_notifications_button,
    #                                            callback_data="switch_notifications"))
    builder.row(types.InlineKeyboardButton(
        text=strings.open_channel, url=conf.channel_link)
    )
    builder.row(types.InlineKeyboardButton(text=strings.vote_button, callback_data="nominations_menu"))
    helper_button = types.InlineKeyboardButton(text=strings.helper_menu_button, callback_data="helper_menu")
    org_button = types.InlineKeyboardButton(text=strings.org_menu_button, callback_data="org_menu")
    match user_group:
        case "helper":
            builder.row(helper_button)
        case "org":
            builder.row(helper_button, org_button)
    # builder.row(types.InlineKeyboardButton(text=strings.update_menu_button, callback_data="main_menu"))
    return builder.as_markup()


def nominations_menu_kb(nominations):
    builder = InlineKeyboardBuilder()
    for nomination in nominations:
        builder.row(types.InlineKeyboardButton(text=nomination.name,
                                               callback_data='category ' + str(nomination.id)))
    builder.row(types.InlineKeyboardButton(text=strings.back_button,
                                           callback_data='main_menu'))
    return builder.as_markup()


def voting_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text=strings.back_button,
                                           callback_data='nominations_menu'))
    return builder.as_markup()


def helper_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text=strings.announce_mode_button,
                                           callback_data='announce_mode'))
    builder.row(types.InlineKeyboardButton(text=strings.back_button,
                                           callback_data='main_menu'))
    return builder.as_markup()


def org_menu_kb(settings: Settings):
    builder = InlineKeyboardBuilder()
    if settings.voting_enabled:
        builder.row(types.InlineKeyboardButton(text=strings.disable_voting,
                                               callback_data='switch_voting'))
    else:
        builder.row(types.InlineKeyboardButton(text=strings.enable_voting,
                                               callback_data='switch_voting'))
    builder.row(types.InlineKeyboardButton(text=strings.back_button,
                                           callback_data='main_menu'))
    return builder.as_markup()


def send_kb(current_position):
    builder = InlineKeyboardBuilder()
    if current_position:
        builder.row(types.InlineKeyboardButton(text=strings.send_button,
                                               callback_data='send_announcement ' + str(current_position)))
    else:
        builder.row(types.InlineKeyboardButton(text=strings.send_button,
                                               callback_data='send_announcement'))
    builder.row(types.InlineKeyboardButton(text=strings.delete_button,
                                           callback_data='delete_message'))
    return builder.as_markup()


def announce_mode_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="Дальше >"))
    builder.row(types.KeyboardButton(text="Вывести ближайшие выступления"))
    builder.row(types.KeyboardButton(text=strings.back_button))
    return builder.as_markup(resize_keyboard=True)
