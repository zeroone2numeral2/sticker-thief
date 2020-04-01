import logging

# noinspection PyPackageRequirements
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    Filters
)
# noinspection PyPackageRequirements
from telegram import ChatAction, Update

from bot import stickersbot
from bot.strings import Strings
from bot.sticker import StickerFile
import bot.sticker.error as error
from ..conversation_statuses import Status
from ..fallback_commands import cancel_command
from ...utils import decorators
from ...utils import utils

logger = logging.getLogger(__name__)


@decorators.action(ChatAction.TYPING)
@decorators.restricted
@decorators.failwithmessage
@decorators.logconversation
def on_remove_command(update: Update, _):
    logger.info('/remove')

    update.message.reply_text(Strings.REMOVE_STICKER_SELECT_STICKER)

    return Status.WAITING_STICKER


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
@decorators.logconversation
def on_sticker_receive(update: Update, context: CallbackContext):
    logger.info('user sent the stciker to add')

    sticker = StickerFile(update.message.sticker)

    pack_link = utils.name2link(update.message.sticker.set_name)

    try:
        sticker.remove_from_set(context.bot)
    except error.PackInvalid:
        update.message.reply_html(Strings.REMOVE_STICKER_FOREIGN_PACK.format(pack_link), quote=True)
    except error.PackNotModified:
        update.message.reply_html(Strings.REMOVE_STICKER_ALREADY_DELETED.format(pack_link), quote=True)
    except error.UnknwonError as e:
        update.message.reply_html(Strings.REMOVE_STICKER_GENERIC_ERROR.format(pack_link, e.message), quote=True)
    else:
        # success
        update.message.reply_html(Strings.REMOVE_STICKER_SUCCESS.format(pack_link), quote=True)
    finally:
        # wait for other stickers
        return Status.WAITING_STICKER


stickersbot.add_handler(ConversationHandler(
    name='adding_stickers',
    # persistent=True,  # do not make this conversation persistent
    entry_points=[CommandHandler(['remove', 'rem', 'r'], on_remove_command)],
    states={
        Status.WAITING_STICKER: [MessageHandler(
            Filters.sticker | Filters.document.category('image/png'),
            on_sticker_receive
        )]
    },
    fallbacks=[CommandHandler(['cancel', 'c', 'done', 'd'], cancel_command)]
))
