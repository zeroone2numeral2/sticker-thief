from telegram.ext import PicklePersistence

from .utils import utils
from .database import base
from .bot import StickersBot
from config import config


stickersbot = StickersBot(
    token=config.telegram.token,
    use_context=True,
    persistence=PicklePersistence(
        filename='persistence/data.pickle',
        store_chat_data=False,
        store_bot_data=False
    ) if config.telegram.get('persistent_temp_data', True) else None,
    workers=1
)


def main():
    utils.load_logging_config('logging.json')

    stickersbot.import_handlers(r'bot/handlers/')
    stickersbot.run(clean=True)


if __name__ == '__main__':
    main()
