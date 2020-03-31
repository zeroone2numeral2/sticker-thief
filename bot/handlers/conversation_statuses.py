class Status:
    # it's important the handlers of the 'create' and 'add' modules
    # return the same statuses because they share com handlers
    WAITING_TITLE = 1
    WAITING_NAME = 2
    WAITING_FIRST_STICKER = 3
    WAITING_STATIC_STICKERS = 4
    WAITING_ANIMATED_STICKERS = 5


STATUSES_DICT = {
    1: 'WAITING_TITLE',
    2: 'WAITING_NAME',
    3: 'WAITING_FIRST_STICKER',
    4: 'WAITING_STATIC_STICKERS',
    5: 'WAITING_ANIMATED_STICKERS'
}


def get_status_description(status_value):
    return STATUSES_DICT.get(status_value, 'unmapped value')
