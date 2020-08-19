# noinspection PyPackageRequirements
from telegram import InlineKeyboardMarkup, InlineKeyboardButton


class InlineKeyboard:
    HIDE = None
    REMOVE = None

    @staticmethod
    def static_animated_switch(animated=False):
        static_button = InlineKeyboardButton(
            '{} normal'.format('☑️' if animated else '✅'),
            callback_data='packtype:static'
        )
        animated_button = InlineKeyboardButton(
            '{} animated'.format('✅' if animated else '☑️'),
            callback_data='packtype:animated'
        )

        return InlineKeyboardMarkup([[static_button, animated_button]])
