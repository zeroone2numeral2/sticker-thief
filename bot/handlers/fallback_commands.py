import logging

# noinspection PyPackageRequirements
from telegram.ext import ConversationHandler, CallbackContext
# noinspection PyPackageRequirements
from telegram import Update, ChatAction

from bot.markups import Keyboard
from bot.strings import Strings
from ..utils import decorators

logger = logging.getLogger(__name__)

STANDARD_CANCEL_COMMANDS = ['cancel', 'c', 'done', 'd']


@decorators.action(ChatAction.TYPING)
@decorators.restricted
@decorators.failwithmessage
@decorators.logconversation
def cancel_command(update: Update, context: CallbackContext):
    logger.info('%s command', update.message.text)

    update.message.reply_text(Strings.CANCEL, reply_markup=Keyboard.HIDE)

    # remove temporary data
    context.user_data.pop('pack', None)
    
    return ConversationHandler.END


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
@decorators.logconversation
def on_timeout(update: Update, context: CallbackContext):
    logger.debug('conversation timeout')

    # remove temporary data
    context.user_data.pop('pack', None)

    update.message.reply_text(Strings.TIMEOUT)

    return ConversationHandler.END
