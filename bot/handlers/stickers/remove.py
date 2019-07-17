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
from ..fallback_commands import cancel_command
from ...utils import decorators
from ...utils import utils

logger = logging.getLogger(__name__)

WAITING_STICKERS = range(1)


@decorators.action(ChatAction.TYPING)
@decorators.restricted
@decorators.failwithmessage
def on_remove_command(update: Update, _):
    logger.info('%d: /remove', update.effective_user.id)

    update.message.reply_text(Strings.REMOVE_STICKER_SELECT_STICKER)

    return WAITING_STICKERS


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
def on_sticker_receive(update: Update, context: CallbackContext):
    logger.info('%d: user sent the stciker to add', update.effective_user.id)

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
        return WAITING_STICKERS


stickersbot.add_handler(ConversationHandler(
    name='adding_stickers',
    entry_points=[CommandHandler(['remove', 'rem', 'r'], on_remove_command)],
    states={
        WAITING_STICKERS: [MessageHandler(
            Filters.sticker | Filters.document.category('image/png'),
            on_sticker_receive
        )]
    },
    fallbacks=[CommandHandler(['cancel', 'c', 'done', 'd'], cancel_command)]
))
