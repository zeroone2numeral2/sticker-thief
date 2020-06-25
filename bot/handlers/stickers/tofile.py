import logging

# noinspection PyPackageRequirements
from telegram.ext import MessageHandler, Filters, CallbackContext
# noinspection PyPackageRequirements
from telegram import Update, ChatAction

from bot import stickersbot
from bot.sticker import StickerFile
from bot.strings import Strings
from ...customfilters import CustomFilters
from ...utils import decorators

logger = logging.getLogger(__name__)


@decorators.restricted
@decorators.action(ChatAction.UPLOAD_DOCUMENT)
@decorators.failwithmessage
def on_animated_sticker_receive(update: Update, context: CallbackContext):
    logger.info('user sent an animated stciker to convert')

    sticker = StickerFile(context.bot, update.message)
    sticker.download(prepare_png=False)

    sent_message = update.message.reply_document(
        sticker.tgs_file,
        filename=update.message.sticker.file_id + '.tgs',
        caption=''.join(sticker.emojis),
        quote=True
    )
    sticker.close()

    if sent_message.document:
        sent_message.reply_html(Strings.TO_DOCUMENT_DEBUG.format(sent_message.document.mime_type), quote=True)


@decorators.restricted
@decorators.action(ChatAction.UPLOAD_DOCUMENT)
@decorators.failwithmessage
def on_static_sticker_receive(update: Update, context: CallbackContext):
    logger.info('user sent a static stciker, we will return it as a file + its emojis')

    sticker = StickerFile(context.bot, update.message)
    sticker.download(prepare_png=True)

    update.message.reply_document(
        sticker.png_file,
        filename=update.message.sticker.file_id + '.png',
        caption=''.join(sticker.emojis),
        quote=True
    )

    sticker.close()


stickersbot.add_handler(MessageHandler(CustomFilters.static_sticker, on_static_sticker_receive))
stickersbot.add_handler(MessageHandler(Filters.sticker, on_animated_sticker_receive))
