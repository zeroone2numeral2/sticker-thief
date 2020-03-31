class Status:
    # it's important the handlers of the 'create' and 'add' modules
    # return the same statuses because they share com handlers
    END = -1  # this is the value of ConversationHandler.END
    WAITING_TITLE = 1
    WAITING_NAME = 2
    WAITING_FIRST_STICKER = 3
    WAITING_STATIC_STICKERS = 4
    WAITING_ANIMATED_STICKERS = 5
    WAITING_STICKER = 6  # any sticker


STATUSES_DICT = {
    Status.END: 'conversation ended',
    Status.WAITING_TITLE: 'WAITING_TITLE',
    Status.WAITING_NAME: 'WAITING_NAME',
    Status.WAITING_FIRST_STICKER: 'WAITING_FIRST_STICKER',
    Status.WAITING_STATIC_STICKERS: 'WAITING_STATIC_STICKERS',
    Status.WAITING_ANIMATED_STICKERS: 'WAITING_ANIMATED_STICKERS',
    Status.WAITING_STICKER: 'WAITING_STICKER'
}


def get_status_description(status_value):
    return STATUSES_DICT.get(status_value, 'unmapped value')
