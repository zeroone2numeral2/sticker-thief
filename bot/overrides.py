# noinspection PyPackageRequirements
from telegram.ext import BaseFilter, Filters


class _Media(BaseFilter):
    name = 'Filters.media'

    def filter(self, message):
        return any([message.audio, message.document, message.photo, message.video, message.video_note, message.voice,
                    message.sticker])


class _Png(BaseFilter):
    name = 'Filters.png'

    def filter(self, message):
        return bool(message.document and message.document.mime_type == 'image/png')


Filters.media = _Media()
Filters.png = _Png()
