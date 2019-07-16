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
from bot.utils import decorators
from bot.strings import Strings
from config import config

logger = logging.getLogger(__name__)


@decorators.action(ChatAction.TYPING)
@decorators.restricted
@decorators.failwithmessage
def on_help_command(update: Update, context: CallbackContext):
    logger.info('%d: /help', update.effective_user.id)

    update.message.reply_html(Strings.HELP_MESSAGE.format(context.bot.username))


@decorators.action(ChatAction.TYPING)
@decorators.restricted
@decorators.failwithmessage
def on_start_command(update: Update, _):
    logger.info('%d: /start', update.effective_user.id)

    start_message = Strings.START_MESSAGE
    if config.bot.sourcecode:
        start_message = '{}\n\n<a href="{}">source code</a>'.format(start_message, config.bot.sourcecode)

    update.message.reply_html(start_message, disable_web_page_preview=True)


stickersbot.add_handler(CommandHandler('help', on_help_command))
stickersbot.add_handler(CommandHandler('start', on_start_command))
