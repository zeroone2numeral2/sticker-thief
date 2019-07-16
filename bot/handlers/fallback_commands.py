import logging

# noinspection PyPackageRequirements
from telegram.ext import ConversationHandler, CallbackContext
# noinspection PyPackageRequirements
from telegram import Update, ChatAction

from ..utils import decorators
from bot import markups as rm
from bot.strings import Strings

logger = logging.getLogger(__name__)


@decorators.action(ChatAction.TYPING)
@decorators.restricted
@decorators.failwithmessage
def cancel_command(update: Update, context: CallbackContext):
    logger.info('%s command', update.message.text)

    update.message.reply_text(Strings.CANCEL, reply_markup=rm.HIDE)

    # remove temporary data
    context.user_data.pop('pack', None)
    
    return ConversationHandler.END
