import logging
import re
from functools import wraps
from html import escape as html_escape

import emoji

from config import config

logger = logging.getLogger(__name__)

API_EXCEPTIONS = {
    10: 'sticker set name is already occupied',
    11: 'STICKERSET_INVALID',  # eg. trying to remove a sticker from a set the bot doesn't own
    12: 'STICKERSET_NOT_MODIFIED',
    13: 'sticker set name invalid',  # eg. starting with a number
    14: 'STICKERS_TOO_MUCH',  # pack is full
    15: 'file is too big',  # png size > 350 kb
    # 16: 'Stickerset_invalid'  # pack name doesn't exist, or pack has been deleted
    17: 'Sticker_png_dimensions'  # invalid png size
}


def get_exception_code(error_message):
    error_message = str(error_message)
    for code, desc in API_EXCEPTIONS.items():
        if re.search(desc, error_message, re.I):
            return code

    return 0


def name2link(name):
    return 'https://t.me/addstickers/{}'.format(name)


def get_emojis(text):
    return ''.join(c for c in text if c in emoji.UNICODE_EMOJI)


def action(chat_action):
    def real_decorator(func):
        @wraps(func)
        def wrapped(update, context, *args, **kwargs):
            context.bot.send_chat_action(update.effective_chat.id, chat_action)
            return func(update, context, *args, **kwargs)

        return wrapped

    return real_decorator


def failwithmessage(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        try:
            return func(update, context, *args, **kwargs)
        except Exception as e:
            logger.error('error while running handler callback: %s', str(e), exc_info=True)
            text = 'An error occurred while processing the message: <code>{}</code>'.format(html_escape(str(e)))
            if update.callback_query:
                update.callback_query.message.reply_html(text)
            else:
                update.message.reply_html(text)

    return wrapped


def restricted(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if config.telegram.admins_only and user_id not in config.telegram.admins:
            logger.info('unauthorized access denied for %d', user_id)
            update.message.reply_text('You are not allowed to use this bot')
            return
        return func(update, context, *args, **kwargs)

    return wrapped


def adminsonly(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in config.telegram.admins:
            logger.warning('user %d tried to use a restriced command', user_id)
            update.message.reply_text('You are not allowed to use this command')
            return
        return func(update, context, *args, **kwargs)

    return wrapped
