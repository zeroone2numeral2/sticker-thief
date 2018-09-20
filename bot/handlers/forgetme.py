import logging

from telegram.ext import CommandHandler
from telegram import ChatAction

from bot import strings as s
from bot import u
from bot import db

logger = logging.getLogger(__name__)


@u.action(ChatAction.TYPING)
@u.restricted
@u.failwithmessage
def on_forgetme_command(bot, update):
    logger.info('%d: /forgetme', update.effective_user.id)

    deleted_rows = db.delete_user_packs(update.effective_user.id)
    logger.info('deleted rows: %d', deleted_rows or 0)

    update.message.reply_text(s.FORGETME_SUCCESS)


HANDLERS = (
    CommandHandler(['forgetme', 'fm'], on_forgetme_command),
)
