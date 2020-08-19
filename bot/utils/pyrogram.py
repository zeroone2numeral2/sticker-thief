import logging

from pyrogram import Client
from pyrogram import Sticker
from pyrogram.api.functions.messages import GetStickerSet
from pyrogram.api.types import InputStickerSetShortName
from pyrogram.api.types import DocumentAttributeSticker
from pyrogram.api.types import DocumentAttributeImageSize
from pyrogram.api.types import DocumentAttributeFilename
# noinspection PyPackageRequirements
from telegram import Message

from .helpers.utils import get_emojis_from_message
from config import config

logger = logging.getLogger(__name__)


class FakeClient:
    def __init__(self):
        pass

    def start(self):
        pass


if all((config.pyrogram.enabled, config.pyrogram.api_id, config.pyrogram.api_hash)):
    client = Client(
        'stickers-bot',
        bot_token=config.telegram.token,
        api_id=config.pyrogram.api_id,
        api_hash=config.pyrogram.api_hash,
        workers=0,
        no_updates=True
    )
else:
    client = FakeClient()


def unpack_document_attributes(document):
    sticker_attributes, image_size_attributes, file_name = None, None, None
    for attribute in document.attributes:
        if isinstance(attribute, DocumentAttributeSticker):
            sticker_attributes = attribute
        elif isinstance(attribute, DocumentAttributeImageSize):
            image_size_attributes = attribute
        elif isinstance(attribute, DocumentAttributeFilename):
            file_name = attribute.file_name

    return sticker_attributes, image_size_attributes, file_name


def get_set_emojis_dict(set_name: str) -> dict:
    input_sticker_set_short_name = InputStickerSetShortName(short_name=set_name)
    sticker_set = client.send(GetStickerSet(stickerset=input_sticker_set_short_name))

    result_dict = dict()

    for document in sticker_set.documents:
        # sticker_set.documents: list of stickers in the pack

        sticker_attributes, image_size_attributes, file_name = unpack_document_attributes(document)

        # noinspection PyProtectedMember
        sticker = Sticker._parse(
            sticker=document,
            image_size_attributes=image_size_attributes,
            sticker_attributes=sticker_attributes,
            file_name=file_name,
            client=client
        )

        result_dict[sticker.file_id] = dict(
            file_id=sticker.file_id,
            document_id=document.id
        )

        # logger.debug('id: %d', document.id)
        # logger.debug('main: %s', sticker_attributes.alt)  # 'alt' actually contains the pack's main emoji

        # each pack in sticker_set.packs is an emoji. A pack has a 'documents' attribute, which contains
        # a list of document ids bound to that emoji
        all_sticker_emojis = list()
        for emoji in sticker_set.packs:
            for document_id in emoji.documents:
                if document_id == document.id:
                    all_sticker_emojis.append(emoji.emoticon)

        # logger.debug('all: %s', all_sticker_emojis)
        result_dict[sticker.file_id]['emojis'] = all_sticker_emojis

    return result_dict


def get_emojis_from_pack(message: Message) -> list:
    if isinstance(client, FakeClient):
        return [message.sticker.emoji]

    sticker = client.get_messages(message.chat.id, message.message_id).sticker

    input_sticker_set_short_name = InputStickerSetShortName(short_name=message.sticker.set_name)
    sticker_set = client.send(GetStickerSet(stickerset=input_sticker_set_short_name))
    # print(sticker_set.documents)

    for document in sticker_set.documents:
        # sticker_set.documents: list of stickers in the pack

        sticker_attributes, image_size_attributes, file_name = unpack_document_attributes(document)

        # noinspection PyProtectedMember
        pack_sticker = Sticker._parse(
            sticker=document,
            image_size_attributes=image_size_attributes,
            sticker_attributes=sticker_attributes,
            file_name=file_name,
            client=client
        )
        if pack_sticker.file_id != sticker.file_id:
            # these two won't be the same: one is from pyrogram, the other one is from the bot api
            # logger.debug('file_id match failed: %s', pack_sticker.file_id)
            continue

        # logger.debug('id: %d', document.id)
        # logger.debug('main: %s', sticker_attributes.alt)  # 'alt' actually contains the pack's main emoji

        # each pack in sticker_set.packs is an emoji. A pack has a 'documents' attribute, which contains
        # a list of document ids bound to that emoji
        all_sticker_emojis = list()
        for emoji in sticker_set.packs:
            for document_id in emoji.documents:
                if document_id == document.id:
                    all_sticker_emojis.append(emoji.emoticon)

        logger.debug('all: %s', all_sticker_emojis)

        return all_sticker_emojis


def get_sticker_emojis(message: Message, use_pyrogram=True) -> list:
    """Will return a list of emojis, or None. If the message has a sticker, it will return the sticker's main emoji (or
    the full emojis list if configured to use pyrogram); if the message is a document, it will return the list of
    emojis in the caption (or None)"""

    if isinstance(client, FakeClient) or not use_pyrogram or message.document:
        # this function will also search a document's caption for emojis
        return get_emojis_from_message(message)

    try:
        logger.debug('trying to get emojis with pyrogram')
        emojis = get_emojis_from_pack(message)
        if not emojis:
            raise ValueError('trying to get the emojis with pyrogram returned None')

        return emojis
    except Exception as e:
        logger.error('error while fetching a sticker\'s emojis list with pyrogram: %s', str(e), exc_info=True)
        return get_emojis_from_message(message)
