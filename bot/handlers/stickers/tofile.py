import logging

# noinspection PyPackageRequirements
from telegram.ext import MessageHandler, Filters
# noinspection PyPackageRequirements
from telegram import Update, ChatAction

from bot import stickersbot
from bot.strings import Strings
from bot.sticker import StickerFile
from ...customfilters import CustomFilters
from ...utils import decorators

logger = logging.getLogger(__name__)


@decorators.restricted
@decorators.action(ChatAction.UPLOAD_DOCUMENT)
@decorators.failwithmessage
def on_static_sticker_receive(update: Update, _):
    logger.info('user sent a static stciker to convert')

    sticker = StickerFile(update.message.sticker)
    sticker.download(prepare_png=True)

    update.message.reply_document(sticker.png_file, filename=update.message.sticker.file_id + '.png', quote=True)

    sticker.close()


@decorators.restricted
@decorators.action(ChatAction.UPLOAD_DOCUMENT)
@decorators.failwithmessage
def on_animated_sticker_receive(update: Update, _):
    logger.info('user sent an animated stciker to convert')

    # sending an animated sticker's .tgs file with send_document sends it as animated sticker
    update.message.reply_text(Strings.ANIMATED_STICKERS_NO_FILE, quote=True)
    return

    sticker = StickerFile(update.message.sticker)
    sticker.download(prepare_png=False)

    update.message.reply_document(sticker.tgs_file, filename=update.message.sticker.file_id + '.tgs', quote=True)

    sticker.close()


stickersbot.add_handler(MessageHandler(CustomFilters.static_sticker, on_static_sticker_receive))
stickersbot.add_handler(MessageHandler(Filters.sticker, on_animated_sticker_receive))
