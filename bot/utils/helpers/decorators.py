import logging
import time
from functools import wraps
from html import escape as html_escape
import uuid

# noinspection PyPackageRequirements
from telegram import Update
# noinspection PyPackageRequirements
from telegram.ext import CallbackContext, ConversationHandler
from sqlalchemy.exc import SQLAlchemyError

from bot.database.base import Session
from bot.handlers.conversation_statuses import get_status_description
from config import config

logger = logging.getLogger(__name__)
loggerc = logging.getLogger('conversation')


def action(chat_action):
    def real_decorator(func):
        @wraps(func)
        def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
            context.bot.send_chat_action(update.effective_chat.id, chat_action)
            return func(update, context, *args, **kwargs)

        return wrapped

    return real_decorator


def logconversation(func):
    @wraps(func)
    def wrapped(update: Update, context: CallbackContext, *args, **kwargs):
        # this is to anonimize logs
        uuid_data = context.user_data.get('uuid_data', False)
        if not uuid_data:
            context.user_data['uuid_data'] = dict(uuid=uuid.uuid4(), generated=time.time())
        else:
            # re-generate uuid after 12 hours (43200 seconds)
            now = time.time()
            if now - context.user_data['uuid_data']['generated'] > 43200:
                context.user_data['uuid_data'] = dict(uuid=uuid.uuid4(), generated=now)

        step_returned = func(update, context, *args, **kwargs)
        loggerc.debug(
            'user %d: function <%s> returned step %d (%s)',
            context.user_data['uuid_data']['uuid'],
            func.__name__,
            step_returned,
            get_status_description(step_returned)
        )

        return step_returned

    return wrapped


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
