# noinspection PyPackageRequirements
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)

HIDE = ReplyKeyboardRemove()


def get_markup_from_list(titles, add_back_button=False):
    if add_back_button:
        titles.append('GO BACK')

    return ReplyKeyboardMarkup([[title] for title in titles], resize_keyboard=True)
