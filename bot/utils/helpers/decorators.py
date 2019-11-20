import logging
from functools import wraps
from html import escape as html_escape

# noinspection PyPackageRequirements
from telegram import Update
# noinspection PyPackageRequirements
from telegram.ext import CallbackContext, ConversationHandler
from sqlalchemy.exc import SQLAlchemyError

from bot.database.base import Session
from config import config

logger = logging.getLogger(__name__)


def action(chat_action):
    def real_decorator(func):
        @wraps(func)
        def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
            context.bot.send_chat_action(update.effective_chat.id, chat_action)
            return func(update, context, *args, **kwargs)

        return wrapped

    return real_decorator


def failwithmessage(func):
    @wraps(func)
    def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        try:
            return func(update, context, *args, **kwargs)
        except Exception as e:
            logger.error('error while running handler callback: %s', str(e), exc_info=True)
            text = 'An error occurred while processing the message: <code>{}</code>'.format(html_escape(str(e)))
            if config.bot.sourcecode:
                text += '\nIf you think this is a bug, please report the issue <a href="{}">here</a>!'.format(config.bot.issues)
            if update.callback_query:
                update.callback_query.message.reply_html(text, disable_web_page_preview=True)
            else:
                update.message.reply_html(text, disable_web_page_preview=True)

            return ConversationHandler.END

    return wrapped


def restricted(func):
    @wraps(func)
    def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        if config.telegram.admins_only and user_id not in config.telegram.admins:
            logger.info('unauthorized access denied for %d', user_id)
            update.message.reply_text('You are not allowed to use this bot')
            return
        return func(update, context, *args, **kwargs)

    return wrapped


def adminsonly(func):
    @wraps(func)
    def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in config.telegram.admins:
            logger.warning('user %d tried to use a restriced command', user_id)
            update.message.reply_text('You are not allowed to use this command')
            return
        return func(update, context, *args, **kwargs)

    return wrapped


# it is not a good idea to use this, because we keep the session open for the whole
# callback execution (api requests included)
def dbsession(func):
    @wraps(func)
    def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        session = Session()

        try:
            callback_result = func(update, context, session=session, *args, **kwargs)
        except SQLAlchemyError:
            session.rollback()
            return

        session.commit()

        return callback_result

    return wrapped
