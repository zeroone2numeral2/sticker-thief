import logging

# noinspection PyPackageRequirements
from telegram.ext import (
    CallbackContext,
    CommandHandler
)
# noinspection PyPackageRequirements
from telegram import (
    ChatAction,
    Update
)

from bot import stickersbot
from bot.utils.decorators import (
    action,
    restricted,
    failwithmessage
)
from bot import db
from bot import strings as s
from config import config

logger = logging.getLogger(__name__)


@action(ChatAction.TYPING)
@restricted
@failwithmessage
def on_help_command(update: Update, context: CallbackContext):
    logger.info('%d: /help', update.effective_user.id)

    update.message.reply_html(s.HELP_MESSAGE.format(context.bot.username))


@action(ChatAction.TYPING)
@restricted
@failwithmessage
def on_start_command(update: Update, context: CallbackContext):
    logger.info('%d: /start', update.effective_user.id)

    db.insert_user(update.effective_user.id)
    start_message = s.START_MESSAGE
    if config.bot.sourcecode:
        start_message = '{}\n\n<a href="{}">source code</a>'.format(start_message, config.bot.sourcecode)

    update.message.reply_html(start_message, disable_web_page_preview=True)


stickersbot.add_handler(CommandHandler('help', on_help_command))
stickersbot.add_handler(CommandHandler('start', on_start_command))
