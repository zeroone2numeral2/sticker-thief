# noinspection PyPackageRequirements
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove


class Keyboard:
    HIDE = ReplyKeyboardRemove()

    @staticmethod
    def from_list(titles, add_back_button=False):
        if add_back_button:
            titles.append('GO BACK')

        return ReplyKeyboardMarkup([[title] for title in titles], resize_keyboard=True)
