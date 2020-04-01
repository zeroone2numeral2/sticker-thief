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


class InvalidAnimatedSticker(StickerError):
    pass


class UnknwonError(StickerError):
    pass


EXCEPTIONS = {
    # pack name is already used
    'sticker set name is already occupied': NameAlreadyOccupied,

    # the bot doesn't own the pack/pack name doesn't exist/pack has been deleted
    'STICKERSET_INVALID': PackInvalid,
    'Stickerset_invalid': PackInvalid,  # new exception description

    'STICKERSET_NOT_MODIFIED': PackNotModified,

    # invalid pack name, eg. starting with a number
    'sticker set name invalid': NameInvalid,

    # pack is full
    'Stickers_too_much': PackFull,  # old exception description
    'Stickerpack_stickers_too_much': PackFull,  # new exception description

    # png size > 350 kb
    'file is too big': FileTooBig,

    # invalid png size
    'Sticker_png_dimensions': FileDimensionInvalid,

    # this happens when we receive an animated sticker which is no longer compliant with the current specifications
    # it also should have as mime type "application/x-bad-tgsticker"
    # https://core.telegram.org/animated_stickers
    'Wrong file type': InvalidAnimatedSticker,

    # not an actual API exception, we reiase it when we receive an unknown exception
    'ext_unknown_api_exception': UnknwonError
}
