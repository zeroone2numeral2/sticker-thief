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
from bot.stickers import StickerFile
from .fallback_commands import cancel_command
from ..utils import decorators
from ..utils import utils

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

    error = sticker.remove_from_set(context.bot)
    pack_link = utils.name2link(update.message.sticker.set_name)
    if not error:
        update.message.reply_html(Strings.REMOVE_STICKER_SUCCESS.format(pack_link), quote=True)
    elif error == 11:
        update.message.reply_html(Strings.REMOVE_STICKER_FOREIGN_PACK.format(utils.name2link(update.message.sticker.set_name)),
                                  quote=True)
    elif error == 12:
        update.message.reply_html(Strings.REMOVE_STICKER_ALREADY_DELETED.format(pack_link), quote=True)
    else:
        update.message.reply_html(Strings.REMOVE_STICKER_GENERIC_ERROR.format(pack_link, error), quote=True)

    # wait for other stickers


stickersbot.add_handler(ConversationHandler(
    name='adding_stickers',
    entry_points=[CommandHandler(['remove', 'rem', 'r'], on_remove_command)],
    states={
        WAITING_STICKERS: [MessageHandler((Filters.sticker | Filters.png), on_sticker_receive)]
    },
    fallbacks=[CommandHandler(['cancel', 'c', 'done', 'd'], cancel_command)]
))
