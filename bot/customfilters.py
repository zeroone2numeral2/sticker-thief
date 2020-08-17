# noinspection PyPackageRequirements
import re

from telegram.ext import BaseFilter


class AnimatedSticker(BaseFilter):
    def filter(self, message):
        if message.sticker and message.sticker.is_animated:
            return True


class StaticSticker(BaseFilter):
    def filter(self, message):
        if message.sticker and not message.sticker.is_animated:
            return True


class Cancel(BaseFilter):
    def filter(self, message):
        if message.text and re.search(r'/cancel\b', message.text, re.I):
            return True


class Done(BaseFilter):
    def filter(self, message):
        if message.text and re.search(r'/done\b', message.text, re.I):
            return True


class DoneOrCancel(BaseFilter):
    def filter(self, message):
        if message.text and re.search(r'/(?:done|cancel)\b', message.text, re.I):
            return True


class CustomFilters:
    animated_sticker = AnimatedSticker()
    static_sticker = StaticSticker()
    cancel = Cancel()
    done = Done()
    done_or_cancel = DoneOrCancel()
