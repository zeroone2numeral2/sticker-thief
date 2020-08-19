import logging

# noinspection PyPackageRequirements
from telegram.ext import ConversationHandler, CallbackContext, CommandHandler
# noinspection PyPackageRequirements
from telegram import Update, ChatAction

from bot import stickersbot
from bot.markups import Keyboard
from bot.strings import Strings
from .fallback_commands import STANDARD_CANCEL_COMMANDS
from ..utils import decorators

logger = logging.getLogger(__name__)


@decorators.action(ChatAction.TYPING)
@decorators.restricted
@decorators.failwithmessage
@decorators.logconversation
def cancel_command_no_conversation(update: Update, context: CallbackContext):
    logger.info('%s command outside of a conversation', update.message.text)

    update.message.reply_text(Strings.CANCEL_NO_CONVERSATION, reply_markup=Keyboard.HIDE)

    # remove temporary data
    context.user_data.pop('pack', None)

    return ConversationHandler.END


# this handler MUST be added AFTER all the ConversationHandler that use the 'cancel_command' function as
# fallback handler
stickersbot.add_handler(CommandHandler(STANDARD_CANCEL_COMMANDS, cancel_command_no_conversation))