import logging
import os
from shutil import rmtree

# noinspection PyPackageRequirements
from telegram.ext import CommandHandler
# noinspection PyPackageRequirements
from telegram import Update

from bot import stickersbot
from bot.utils import decorators

logger = logging.getLogger(__name__)


@decorators.restricted
@decorators.adminsonly
@decorators.failwithmessage
def on_del_command(update: Update, _):
    logger.info('%d: /deltmp', update.effective_user.id)

    tmp_dir = 'tmp/'
    entries = [entry for entry in os.listdir(tmp_dir) if not entry.startswith('.')]
    update.message.reply_text('Deleting {} files/directories...'.format(len(entries)))

    for entry in entries:
        entry_path = os.path.join(tmp_dir, entry)
        if os.path.isfile(entry_path):
            os.unlink(entry_path)
        else:
            rmtree(entry_path)

    update.message.reply_text('...done')


stickersbot.add_handler(CommandHandler(['deltmp', 'del'], on_del_command))
