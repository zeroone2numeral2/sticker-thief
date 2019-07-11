import importlib
import logging
import logging.config
import json

from bot import dispatcher
from bot import updater
from bot.priority import HANDLER as PRIORITY_HANDLER
from config import HANDLERS

logger = logging.getLogger(__name__)


def load_logging_config(file_path='logging.json'):
    with open(file_path, 'r') as f:
        logging_config = json.load(f)

    logging.config.dictConfig(logging_config)


load_logging_config()


def error_callback(bot, update, error):
    logger.info('Update: %s\nerror: %s', update, error, exc_info=True)


def main():
    logger.info('adding special priority handler...')
    dispatcher.add_handler(PRIORITY_HANDLER, group=0)

    logger.info('registering handlers...')
    for modname in HANDLERS:
        handlers = getattr(importlib.import_module('bot.handlers.{}'.format(modname)), 'HANDLERS')
        logger.info('importing module: %s (handlers: %d)', modname, len(handlers))
        for handler in handlers:
            dispatcher.add_handler(handler, group=1)

    dispatcher.add_error_handler(error_callback)

    logger.info('starting polling loop as @%s...', updater.bot.username)
    updater.start_polling(clean=True)
    updater.idle()


if __name__ == '__main__':
    main()
