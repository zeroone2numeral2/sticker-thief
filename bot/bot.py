import logging
import os
import importlib
from pathlib import Path

# noinspection PyPackageRequirements
from telegram.ext import Updater, ConversationHandler

logger = logging.getLogger(__name__)


class StickersBot(Updater):
    @staticmethod
    def import_handlers(directory):
        for path in sorted(Path(directory).rglob('*.py')):
            file_path = os.path.splitext(str(path))[0]

            import_path = []

            while file_path:
                file_path, tail = os.path.split(file_path)
                import_path.insert(0, tail)

            import_path = '.'.join(import_path)

            logger.debug('importing module: %s', import_path)
            importlib.import_module(import_path)

    def run(self, *args, **kwargs):
        logger.info('running as @%s', self.bot.username)
        self.start_polling(*args, **kwargs)
        self.idle()

    def add_handler(self, *args, **kwargs):
        if isinstance(args[0], ConversationHandler):
            # ConverstaionHandler.name or the name of the first entry_point function
            logger.info('adding conversation handler: %s', args[0].name or args[0].entry_points[0].callback.__name__)
        else:
            logger.info('adding handler: %s', args[0].callback.__name__)

        self.dispatcher.add_handler(*args, **kwargs)
