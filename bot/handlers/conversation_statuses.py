class Status:
    # it's important the handlers of the 'create' and 'add' modules
    # return the same statuses because they share com handlers
    END = -1  # this is the value of ConversationHandler.END
    TIMEOUT = -2  # this is the value of ConversationHandler.TIMEOUT
    CREATE_WAITING_TITLE = 10
    CREATE_WAITING_NAME = 20
    ADD_WAITING_TITLE = 30
    ADD_WAITING_NAME = 40
    CREATE_WAITING_FIRST_STICKER = 50
    WAITING_STATIC_STICKERS = 60
    WAITING_ANIMATED_STICKERS = 70
    WAITING_STICKER = 80  # any sticker


STATUSES_DICT = {
    Status.END: 'conversation ended',
    Status.TIMEOUT: 'conversation timed out',
    Status.CREATE_WAITING_TITLE: 'CREATE_WAITING_TITLE',
    Status.CREATE_WAITING_NAME: 'CREATE_WAITING_NAME',
    Status.ADD_WAITING_TITLE: 'ADD_WAITING_TITLE',
    Status.ADD_WAITING_NAME: 'ADD_WAITING_NAME',
    Status.CREATE_WAITING_FIRST_STICKER: 'CREATE_WAITING_FIRST_STICKER',
    Status.WAITING_STATIC_STICKERS: 'WAITING_STATIC_STICKERS',
    Status.WAITING_ANIMATED_STICKERS: 'WAITING_ANIMATED_STICKERS',
    Status.WAITING_STICKER: 'WAITING_STICKER'
}


def get_status_description(status_value):
    return STATUSES_DICT.get(status_value, 'unmapped value')
