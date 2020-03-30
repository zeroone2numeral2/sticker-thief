import logging
import math
import re
import tempfile

from PIL import Image
# noinspection PyPackageRequirements
from telegram import Sticker, Document, InputFile
# noinspection PyPackageRequirements
from telegram.error import BadRequest, TelegramError

from ..utils import utils
from .error import EXCEPTIONS

logger = logging.getLogger(__name__)


def get_correct_size(sizes):
    i = 0 if sizes[0] > sizes[1] else 1  # i: index of the biggest size
    new = [None, None]
    new[i] = 512
    rateo = 512 / sizes[i]
    # print(rateo)
    new[1 if i == 0 else 0] = int(math.floor(sizes[1 if i == 0 else 0] * round(rateo, 4)))

    logger.debug('correct sizes: %dx%d', new[0], new[1])
    return tuple(new)


class StickerFile:
    def __init__(self, sticker: [Sticker, Document], animated=False, caption=None, temp_file=None):
        self._animated = animated
        self._file = sticker
        self._emoji = None
        self._size_original = (0, 0)
        self._size_resized = (0, 0)
        self._tempfile_downloaded = temp_file or tempfile.SpooledTemporaryFile()  # webp or tgs files
        self._tempfile_converted = tempfile.SpooledTemporaryFile()  # png file (webp converted to png)

        if isinstance(sticker, Sticker):
            logger.debug('StickerFile object is a Sticker')
            self._is_sticker = True
            self._emoji = sticker.emoji if sticker.emoji is not None else '💈'
        elif isinstance(sticker, Document):
            logger.debug('StickerFile object is a Document')
            self._is_sticker = False
            if caption:
                self._emoji = utils.get_emojis(caption)
            if not self._emoji:
                self._emoji = '💈'

    @property
    def emoji(self):
        return self._emoji

    @property
    def size(self):
        if self._size_resized == (0, 0):
            return self._size_original
        else:
            return self._size_resized

    @property
    def png_file(self):
        self._tempfile_converted.seek(0)
        return self._tempfile_converted

    @property
    def png_input_file(self):
        """returns a telegram InputFile"""
        return InputFile(self.png_file, filename=self._file.file_id + '.png')

    @property
    def tgs_file(self):
        self._tempfile_downloaded.seek(0)  # we don't need to do any further conversion so we can use the downloaded file
        return self._tempfile_downloaded

    @property
    def tgs_input_file(self):
        """returns a telegram InputFile"""
        return InputFile(self.tgs_file, filename=self._file.file_id + '.tgs')

    @staticmethod
    def _raise_exception(received_error_message):
        for expected_api_error_message, exception_to_raise in EXCEPTIONS.items():
            if re.search(expected_api_error_message, received_error_message, re.I):
                raise exception_to_raise(received_error_message)

        # raise unknown error if no description matched
        raise EXCEPTIONS[''](received_error_message)

    def download(self, prepare_png=False):
        logger.debug('downloading sticker')
        new_file = self._file.get_file()

        logger.debug('downloading to bytes object: self._tempfile_downloaded')
        new_file.download(out=self._tempfile_downloaded)
        self._tempfile_downloaded.seek(0)

        if prepare_png and not self._animated:
            return self.prepare_png()

    def prepare_png(self):
        logger.info('preparing png')

        im = Image.open(self._tempfile_downloaded)  # try to open bytes object

        logger.debug('original image size: %s', im.size)
        self._size_original = im.size
        if (im.size[0] > 512 or im.size[1] > 512) or (im.size[0] != 512 and im.size[1] != 512):
            logger.debug('resizing file because one of the sides is > 512px or at least one side is not 512px')
            correct_size = get_correct_size(im.size)
            self._size_resized = correct_size
            im = im.resize(correct_size, Image.ANTIALIAS)
        else:
            logger.debug('original size is ok')

        logger.debug('saving PIL image object as tempfile')
        im.save(self._tempfile_converted, 'png')
        im.close()

        self._tempfile_converted.seek(0)

    def close(self, keep_result_png_open=False):
        # noinspection PyBroadException
        try:
            self._tempfile_downloaded.close()
        except Exception as e:
            logger.error('error while trying to close downloaded tempfile: %s', str(e))

        if not keep_result_png_open and not self._animated:
            # noinspection PyBroadException
            try:
                self._tempfile_converted.close()
            except Exception as e:
                logger.error('error while trying to close result png tempfile: %s', str(e))

    def add_to_set(self, bot, user_id, pack_name):
        logger.debug('adding sticker to set %s', pack_name)

        request_payload = dict(
            user_id=user_id,
            name=pack_name,
            emojis=self._emoji,
            mask_position=None
        )

        if not self._animated:
            request_payload['png_sticker'] = self.png_input_file
        else:
            request_payload['tgs_sticker'] = self.png_input_file

        try:
            bot.add_sticker_to_set(**request_payload)
            logger.debug('...sticker added')
        except (BadRequest, TelegramError) as e:
            logger.error('Telegram exception while trying to add a sticker to %s: %s', pack_name, e.message)
            self._raise_exception(e.message)

    def remove_from_set(self, bot):
        logger.debug('removing sticker from set %s', self._file.set_name)

        try:
            bot.delete_sticker_from_set(self._file.file_id)
            return 0
        except (BadRequest, TelegramError) as e:
            logger.error('Telegram exception while trying to remove a sticker from %s: %s', self._file.set_name,
                         e.message)
            self._raise_exception(e.message)

    @classmethod
    def create_set(cls, bot, *args, **kwargs):
        try:
            return bot.create_new_sticker_set(*args, **kwargs)
        except (BadRequest, TelegramError) as e:
            logger.error('Telegram exception while trying to create a pack: %s', e.message)
            cls._raise_exception(e.message)

    def __repr__(self):
        return 'StickerFile object of original type {} (animated: {}, original size: {}, resized: {})'.format(
            'Sticker' if self._is_sticker else 'Document',
            self._animated,
            self._size_original,
            self._size_resized
        )
