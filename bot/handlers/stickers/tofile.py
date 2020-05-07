import logging

from pyrogram import Client
from pyrogram import Sticker
from pyrogram.api.functions.messages import GetStickerSet
from pyrogram.api.types import InputStickerSetShortName
from pyrogram.api.types import DocumentAttributeSticker
from pyrogram.api.types import DocumentAttributeImageSize
from pyrogram.api.types import DocumentAttributeFilename
# noinspection PyPackageRequirements
from telegram.ext import MessageHandler, Filters
# noinspection PyPackageRequirements
from telegram import Update, ChatAction

from bot import stickersbot
from bot.strings import Strings
from bot.sticker import StickerFile
from ...customfilters import CustomFilters
from ...utils import decorators
from config import config

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

    # sticker = StickerFile(update.message.sticker)
    # sticker.download(prepare_png=False)

    # update.message.reply_document(sticker.tgs_file, filename=update.message.sticker.file_id + '.tgs', quote=True)

    # sticker.close()


@decorators.restricted
@decorators.failwithmessage
def on_static_sticker_return_emojis(update: Update, _):
    logger.info('user sent a static stciker, we will return its emojis (as a test)')

    client = Client(
        'stickers-bot',
        bot_token=config.telegram.token,
        api_id=config.pyrogram.api_id,
        api_hash=config.pyrogram.api_hash,
        workers=0,
        no_updates=True
    )

    with client as c:
        input_sticker_set_short_name = InputStickerSetShortName(short_name=update.message.sticker.set_name)
        sticker_set = c.send(GetStickerSet(stickerset=input_sticker_set_short_name))
        # print(sticker_set.documents)

        print('bot api file_id:', update.message.sticker.file_id)
        for document in sticker_set.documents:
            sticker_attributes = image_size_attributes = file_name = None
            for attribute in document.attributes:
                if isinstance(attribute, DocumentAttributeSticker):
                    sticker_attributes = attribute
                elif isinstance(attribute, DocumentAttributeImageSize):
                    image_size_attributes = attribute
                elif isinstance(attribute, DocumentAttributeFilename):
                    file_name = attribute.file_name

            # noinspection PyProtectedMember
            sticker = Sticker._parse(
                sticker=document,
                image_size_attributes=image_size_attributes,
                sticker_attributes=sticker_attributes,
                file_name=file_name,
                client=c
            )
            if sticker.file_id != update.message.sticker.file_id:
                # these two won't be the same: one is from pyrogram, the other one is from the bot api
                print('file_id match failed:', sticker.file_id)

            print('id:', document.id)
            print('', 'main:', sticker_attributes.alt)  # sticker_attributes.alt actually contains the pack's main emoji

            # each pack in sticker_set.packs is an emoji. A pack has a 'documents' attribute, which contains
            # a list of document ids bound to that emoji
            all_sticker_emojis = list()
            for emoji in sticker_set.packs:
                for document_id in emoji.documents:
                    if document_id == document.id:
                        all_sticker_emojis.append(emoji.emoticon)

            print('', 'all:', ', '.join(all_sticker_emojis))


stickersbot.add_handler(MessageHandler(CustomFilters.static_sticker, on_static_sticker_return_emojis))
stickersbot.add_handler(MessageHandler(CustomFilters.static_sticker, on_static_sticker_receive))
stickersbot.add_handler(MessageHandler(Filters.sticker, on_animated_sticker_receive))
