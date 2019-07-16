import logging

# noinspection PyPackageRequirements
from telegram.ext import CommandHandler
# noinspection PyPackageRequirements
from telegram import ChatAction, Update

from bot import stickersbot
from bot.strings import Strings
from bot.utils import decorators
from bot import db

logger = logging.getLogger(__name__)


@decorators.action(ChatAction.TYPING)
@decorators.restricted
@decorators.failwithmessage
def on_forgetme_command(update: Update, _):
    logger.info('%d: /forgetme', update.effective_user.id)

    deleted_rows = db.delete_user_packs(update.effective_user.id)
    logger.info('deleted rows: %d', deleted_rows or 0)

    update.message.reply_text(Strings.FORGETME_SUCCESS)


stickersbot.add_handler(CommandHandler(['forgetme', 'fm'], on_forgetme_command))
