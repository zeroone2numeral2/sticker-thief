import importlib
import logging
import logging.config

from yaml import safe_load

from bot import dispatcher
from bot import updater
from bot.priority import HANDLER as PRIORITY_HANDLER
from config import config
from config import HANDLERS

if bool(int(config.log.silence_ptb_logger)):
    logging.getLogger('telegram').setLevel(logging.WARNING)
logging.getLogger('PIL').setLevel(logging.WARNING)


def load_logging_config(file_path='logging.yaml'):
    with open(file_path, 'rt') as f:
        logging_config = safe_load(f.read())
        logging_config['handlers']['file']['filename'] = config.log.filename
    logging.config.dictConfig(logging_config)


logger = logging.getLogger(__name__)
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
