# noinspection PyPackageRequirements
from telegram import Message
# noinspection PyPackageRequirements
from telegram.ext import BaseFilter, Filters


class _Png(BaseFilter):
    name = 'Filters.png'

    def filter(self, message: Message):
        return bool(message.document and message.document.mime_type == 'image/png')


Filters.png = _Png()
