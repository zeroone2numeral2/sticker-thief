import logging
import re
import sys
import tempfile

# noinspection PyPackageRequirements
from telegram import Sticker, Document, InputFile, Bot, Message, File
# noinspection PyPackageRequirements
from telegram.error import BadRequest, TelegramError

from ..utils import utils
from ..utils.pyrogram import get_sticker_emojis
from .error import EXCEPTIONS

logger = logging.getLogger('StickerFile')


class StickerFile:
    DEFAULT_EMOJI = '🎭'

    def __init__(self, bot: Bot, message: Message, temp_file=None, emojis: [list, None] = None):
        self._bot = bot
        self._animated = False
        self._sticker = message.sticker or message.document
        self._is_sticker = True
        # self._emojis = get_sticker_emojis(message) or [self.DEFAULT_EMOJI]
        self._size_original = (0, 0)
        self._size_resized = (0, 0)
        self._user_id = message.from_user.id  # we need this in case we have to create a pack or to add to a pack
        self._downloaded_tempfile = temp_file or tempfile.SpooledTemporaryFile()  # webp or tgs files

        if isinstance(self._sticker, Sticker):
            logger.debug('StickerFile object is a Sticker (animated: %s)', self._sticker.is_animated)
            self._is_sticker = True
            self._animated = self._sticker.is_animated
        elif isinstance(self._sticker, Document):
            logger.debug('StickerFile object is a Document')
            self._is_sticker = False

        if emojis:
            # the user sent some emojis before sending the sticker
            self._emojis = emojis
        elif self._is_sticker and not message.sticker.emoji:
            logger.info("the sticker doesn't have a pack, using default emoji")
            self._emojis = [self.DEFAULT_EMOJI]
        else:
            self._emojis = get_sticker_emojis(message) or [self.DEFAULT_EMOJI]

        logger.debug('emojis: %s', self._emojis)

    @property
    def emojis(self):
        if not isinstance(self._emojis, (list, tuple)):
            raise ValueError('StickerFile._emojis is not of type list/tuple (type: {})'.format(type(self._emojis)))

        return self._emojis

    @property
    def emojis_str(self):
        if not isinstance(self._emojis, (list, tuple)):
            raise ValueError('StickerFile._emojis is not of type list/tuple (type: {})'.format(type(self._emojis)))

        return ''.join(self._emojis)

    @property
    def size(self):
        if self._size_resized == (0, 0):
            return self._size_original
        else:
            return self._size_resized

    @property
    def input_file(self):
        """returns a telegram InputFile"""
        extension = '.webp'
        if self._animated:
            extension = '.tgs'

        self._downloaded_tempfile.seek(0)

        return InputFile(self._downloaded_tempfile, filename=self._sticker.file_id + extension)

    @property
    def file_id(self):
        return self._sticker.file_id

    @property
    def tempfile(self):
        self._downloaded_tempfile.seek(0)
        return self._downloaded_tempfile

    @staticmethod
    def _raise_exception(received_error_message):
        for expected_api_error_message, exception_to_raise in EXCEPTIONS.items():
            if re.search(expected_api_error_message, received_error_message, re.I):
                raise exception_to_raise(received_error_message)

        # raise unknown error if no description matched
        logger.info('unknown exception: %s', received_error_message)
        raise EXCEPTIONS['ext_unknown_api_exception'](received_error_message)

    def download(self):
        logger.debug('downloading sticker')
        new_file: File = self._sticker.get_file()

        logger.debug('downloading to bytes object')
        new_file.download(out=self._downloaded_tempfile)
        self._downloaded_tempfile.seek(0)

        if not self._is_sticker:
            self._downloaded_tempfile = utils.resize_png(self._downloaded_tempfile)

    def close(self):
        # noinspection PyBroadException
        try:
            self._downloaded_tempfile.close()
        except Exception as e:
            logger.error('error while trying to close downloaded tempfile: %s', str(e))

    def add_to_set(self, pack_name):
        logger.debug('adding sticker to set %s', pack_name)

        request_payload = dict(
            user_id=self._user_id,
            name=pack_name,
            emojis=''.join(self._emojis),
            mask_position=None
        )

        if not self._animated:
            request_payload['png_sticker'] = self.input_file
        else:
            request_payload['tgs_sticker'] = self.input_file

        try:
            self._bot.add_sticker_to_set(**request_payload)
            logger.debug('...sticker added')
        except (BadRequest, TelegramError) as e:
            logger.error('Telegram exception while trying to add a sticker to %s: %s', pack_name, e.message)
            self._raise_exception(e.message)

    def remove_from_set(self):
        logger.debug('removing sticker from set %s', self._sticker.set_name)

        try:
            self._bot.delete_sticker_from_set(self._sticker.file_id)
            return 0
        except (BadRequest, TelegramError) as e:
            logger.error('Telegram exception while trying to remove a sticker from %s: %s', self._sticker.set_name,
                         e.message)
            self._raise_exception(e.message)

    def create_set(self, title, name, **kwargs):
        request_payload = kwargs
        request_payload['user_id'] = self._user_id
        request_payload['title'] = title
        request_payload['name'] = name

        if self._animated:
            request_payload['tgs_sticker'] = self.input_file
        else:
            # we need to use an input file becase a tempfile.SpooledTemporaryFile has a 'name' attribute which
            # makes python-telegram-bot retrieve the file's path using os (https://github.com/python-telegram-bot/python-telegram-bot/blob/2a3169a22f7227834dd05a35f90306375136e41a/telegram/files/inputfile.py#L58)
            # to populate the 'filename' attribute, which would result an exception since it is
            # a byte object. That means we have to do it ourself by  creating the InputFile and
            # assigning it a custom 'filename'
            request_payload['png_sticker'] = self.input_file

        try:
            return self._bot.create_new_sticker_set(**request_payload)
        except (BadRequest, TelegramError) as e:
            logger.error('Telegram exception while trying to create a pack: %s', e.message)
            self._raise_exception(e.message)

    def __repr__(self):
        return 'StickerFile object of original type {} (animated: {}, original size: {}, resized: {})'.format(
            'Sticker' if self._is_sticker else 'Document',
            self._animated,
            self._size_original,
            self._size_resized
        )
