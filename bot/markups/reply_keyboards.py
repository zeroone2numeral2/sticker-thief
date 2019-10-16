# noinspection PyPackageRequirements
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove


class Keyboard:
    HIDE = ReplyKeyboardRemove()

    @staticmethod
    def from_list(items, add_back_button=False):
        items_copy = [i for i in items]  # we need to create a copy of this list otherwise the back button might be
        if add_back_button:
            items_copy.append('GO BACK')

        return ReplyKeyboardMarkup([[i] for i in items_copy], resize_keyboard=True)
