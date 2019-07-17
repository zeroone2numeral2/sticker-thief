import logging

# noinspection PyPackageRequirements
from telegram.ext import MessageHandler, Filters
# noinspection PyPackageRequirements
from telegram import Update, ChatAction

from bot import stickersbot
from bot.stickers import StickerFile
from ...utils import decorators

logger = logging.getLogger(__name__)


@decorators.restricted
@decorators.action(ChatAction.UPLOAD_DOCUMENT)
@decorators.failwithmessage
def on_sticker_receive(update: Update, _):
    logger.info('%d: user sent a stciker to convert', update.effective_user.id)

    sticker = StickerFile(update.message.sticker)
    sticker.download(prepare_png=True)

    update.message.reply_document(sticker.png_bytes_object, quote=True)

    sticker.delete()


stickersbot.add_handler(MessageHandler(Filters.sticker, on_sticker_receive))
