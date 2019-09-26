# noinspection PyPackageRequirements
from telegram.ext import BaseFilter


class AnimatedSticker(BaseFilter):
    def filter(self, message):
        if message.sticker and message.sticker.is_animated:
            return True


class StaticSticker(BaseFilter):
    def filter(self, message):
        if message.sticker and not message.sticker.is_animated:
            return True


class CustomFilters:
    animated_sticker = AnimatedSticker()
    static_sticker = StaticSticker()
