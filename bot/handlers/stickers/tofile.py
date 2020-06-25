import logging

# noinspection PyPackageRequirements
from telegram.ext import MessageHandler, Filters, CallbackContext
# noinspection PyPackageRequirements
from telegram import Update, ChatAction, Message, ParseMode

from bot import stickersbot
from bot.sticker import StickerFile
from bot.strings import Strings
from ...utils import decorators

logger = logging.getLogger(__name__)


@decorators.restricted
@decorators.action(ChatAction.UPLOAD_DOCUMENT)
@decorators.failwithmessage
def on_sticker_receive(update: Update, context: CallbackContext):
    logger.info('user sent an animated stciker to convert')

    sticker = StickerFile(context.bot, update.message)
    sticker.download(prepare_png=not update.message.sticker.is_animated)

    request_kwargs = dict(
        caption=sticker.emojis_str,
        quote=True
    )

    if update.message.sticker.is_animated:
        request_kwargs['document'] = sticker.tgs_file
        request_kwargs['filename'] = update.message.sticker.file_id + '.json'
    else:
        request_kwargs['document'] = sticker.png_file
        request_kwargs['filename'] = update.message.sticker.file_id + '.png'

    sent_message: Message = update.message.reply_document(**request_kwargs)
    sticker.close()

    sent_message.edit_caption(
        caption='{}\n{}'.format(
            sent_message.caption,
            Strings.TO_FILE_MIME_TYPE.format(sent_message.document.mime_type)
        ),
        parse_mode=ParseMode.HTML
    )


stickersbot.add_handler(MessageHandler(Filters.sticker, on_sticker_receive))
