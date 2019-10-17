import logging

# noinspection PyPackageRequirements
from telegram.ext import CommandHandler
# noinspection PyPackageRequirements
from telegram import ChatAction, Update

from bot import stickersbot
from bot.database.base import session_scope
from bot.database.models.pack import Pack
from bot.strings import Strings
from bot.utils import decorators

logger = logging.getLogger(__name__)


@decorators.action(ChatAction.TYPING)
@decorators.restricted
@decorators.failwithmessage
def on_forgetme_command(update: Update, _):
    logger.info('/forgetme')

    with session_scope() as session:
        deleted_rows = session.query(Pack).filter(Pack.user_id==update.effective_user.id).delete()
        logger.info('deleted rows: %d', deleted_rows or 0)

    update.message.reply_text(Strings.FORGETME_SUCCESS)


stickersbot.add_handler(CommandHandler(['forgetme', 'fm'], on_forgetme_command))
