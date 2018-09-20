import logging
import os
from shutil import rmtree

from telegram.ext import CommandHandler

from bot import u

logger = logging.getLogger(__name__)


@u.restricted
@u.adminsonly
@u.failwithmessage
def on_del_command(bot, update):
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


HANDLERS = (
    CommandHandler(['deltmp', 'del'], on_del_command),
)
