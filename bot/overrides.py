from telegram.ext import BaseFilter
from telegram.ext import Filters


class _Status(BaseFilter):
    name = 'Filters.status'

    def __init__(self, status=[]):
        if isinstance(status, str):
            self.statuses = [status]
        elif isinstance(status, (list, tuple)):
            self.statuses = status

    def filter(self, message):
        if getattr(message.from_user, 'status', None) is None:
            return False
        return bool(message.from_user.status in self.statuses)


class _Media(BaseFilter):
    name = 'Filters.media'

    def filter(self, message):
        return any([message.audio, message.document, message.photo, message.video, message.video_note, message.voice,
                    message.sticker])


class _Png(BaseFilter):
    name = 'Filters.png'

    def filter(self, message):
        return bool(message.document and message.document.mime_type == 'image/png')


Filters.status = _Status
Filters.media = _Media()
Filters.png = _Png()
