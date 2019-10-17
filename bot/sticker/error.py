class StickerError(Exception):
    def __init__(self, message):
        super(StickerError, self).__init__()

        self.message = message

    def __str__(self):
        return '{}'.format(self.message)


class NameAlreadyOccupied(StickerError):
    pass


class PackInvalid(StickerError):
    pass


class PackNotModified(StickerError):
    pass


class NameInvalid(StickerError):
    pass


class PackFull(StickerError):
    pass


class FileTooBig(StickerError):
    pass


class FileDimensionInvalid(StickerError):
    pass


class UnknwonError(StickerError):
    pass


EXCEPTIONS = {
    'sticker set name is already occupied': NameAlreadyOccupied,
    'STICKERSET_INVALID': PackInvalid,  # eg. trying to remove a sticker from a set the bot doesn't own, pack name doesn't exist, or pack has been deleted
    'STICKERSET_NOT_MODIFIED': PackNotModified,
    'sticker set name invalid': NameInvalid,  # eg. starting with a number
    'Stickers_too_much': PackFull,  # pack is full
    'file is too big': FileTooBig,  # png size > 350 kb
    'Sticker_png_dimensions': FileDimensionInvalid,  # invalid png size
    '': UnknwonError
}
