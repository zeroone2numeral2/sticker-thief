import logging

from telegram.ext import MessageHandler
from telegram import ChatAction

from bot.overrides import Filters
from bot import u
from bot import StickerFile

logger = logging.getLogger(__name__)


@u.restricted
@u.action(ChatAction.UPLOAD_DOCUMENT)
@u.failwithmessage
def on_sticker_receive(bot, update):
    logger.info('%d: user sent a stciker to convert', update.effective_user.id)

    sticker = StickerFile(update.message.sticker)
    sticker.download(prepare_png=True)

    update.message.reply_document(sticker.png_bytes_object, quote=True)

    sticker.delete()


HANDLERS = (
    MessageHandler(Filters.sticker & Filters.status(''), on_sticker_receive),
)
