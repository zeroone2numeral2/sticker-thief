import logging

from telegram.ext import CommandHandler
from telegram import ChatAction

from bot import u
from bot import db
from bot import strings as s
from config import config

logger = logging.getLogger(__name__)


@u.action(ChatAction.TYPING)
@u.restricted
@u.failwithmessage
def on_help_command(bot, update):
    logger.info('%d: /help', update.effective_user.id)

    update.message.reply_html(s.HELP_MESSAGE)


@u.action(ChatAction.TYPING)
@u.restricted
@u.failwithmessage
def on_start_command(bot, update):
    logger.info('%d: /start', update.effective_user.id)

    db.insert_user(update.effective_user.id)
    start_message = s.START_MESSAGE
    if config.bot.sourcecode:
        start_message = '{}\n\n<a href="{}">source code</a>'.format(start_message, config.bot.sourcecode)

    update.message.reply_html(start_message, disable_web_page_preview=True)


HANDLERS = (
    CommandHandler('help', on_help_command),
    CommandHandler('start', on_start_command)
)
