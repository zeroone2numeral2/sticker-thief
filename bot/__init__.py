import logging

# noinspection PyUnresolvedReferences,PyPackageRequirements
from telegram.ext import PicklePersistence
# noinspection PyUnresolvedReferences,PyPackageRequirements
from telegram.utils.request import Request

from .utils import utils
from .utils.pyrogram import client
from .database import base
from .bot import StickersBot
from .bot import CustomBot
from config import config

logger = logging.getLogger(__name__)

stickersbot = StickersBot(
    bot=CustomBot(token=config.telegram.token, request=Request(con_pool_size=config.telegram.get('workers', 1) + 4)),
    use_context=True,
    persistence=PicklePersistence(
        filename='persistence/data.pickle',
        store_chat_data=False,
        store_bot_data=False
    ) if config.telegram.get('persistent_temp_data', True) else None,
)


def main():
    utils.load_logging_config('logging.json')

    if config.pyrogram.enabled:
        logger.info('starting pyrogram client...')
        client.start()

    stickersbot.import_handlers(r'bot/handlers/')
    stickersbot.run(clean=True)


if __name__ == '__main__':
    main()
