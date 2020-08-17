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
    logger.info('user sent a sticker to convert')

    if update.message.sticker.is_animated:
        # do nothing with animated stickers. We keep the code here just for debugging purposes
        return

    sticker = StickerFile(context.bot, update.message)
    sticker.download(prepare_png=not update.message.sticker.is_animated)

    request_kwargs = dict(
        caption=sticker.emojis_str,
        quote=True
    )

    if update.message.sticker.is_animated:
        request_kwargs['document'] = sticker.tgs_file
        request_kwargs['filename'] = update.message.sticker.file_id + '.tgs'
    else:
        request_kwargs['document'] = sticker.png_file
        request_kwargs['filename'] = update.message.sticker.file_id + '.png'

    sent_message: Message = update.message.reply_document(**request_kwargs)
    sticker.close()

    if sent_message.document:
        # only do this when we send the message as document
        # it will be useful to test problems with animated stickers. For example in mid 2020, the API started
        # to consider any animated sticker as invalid ("wrong file type" exception), and they were sent
        # back as file with a specific mimetype ("something something bad animated sticker"). In this way:
        # - sent back as animated sticker: everything ok
        # - sent back as file: there's something wrong with the code/api, better to edit the document with its mimetype
        sent_message.edit_caption(
            caption='{}\n<code>{}</code>'.format(
                sent_message.caption,
                Strings.TO_FILE_MIME_TYPE.format(sent_message.document.mime_type)
            ),
            parse_mode=ParseMode.HTML
        )
    elif sent_message.sticker:
        update.message.reply_text(Strings.ANIMATED_STICKERS_NO_FILE)


stickersbot.add_handler(MessageHandler(Filters.sticker, on_sticker_receive))
