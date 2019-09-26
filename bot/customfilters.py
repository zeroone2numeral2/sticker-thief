# noinspection PyPackageRequirements
from telegram.ext import BaseFilter


class AnimatedSticker(BaseFilter):
    def filter(self, message):
        if message.sticker and message.sticker.is_animated:
            return True


animated_sticker = AnimatedSticker()
