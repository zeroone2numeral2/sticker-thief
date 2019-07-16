import logging

# noinspection PyPackageRequirements
from telegram.ext import CommandHandler
# noinspection PyPackageRequirements
from telegram import ChatAction, Update

from bot import stickersbot
from bot.utils import decorators
from bot.utils import utils
from bot import db
from bot import strings as s

logger = logging.getLogger(__name__)


@decorators.action(ChatAction.TYPING)
@decorators.restricted
@decorators.failwithmessage
def on_list_command(update: Update, _):
    logger.info('%d: /list', update.effective_user.id)

    packs = db.get_user_packs(update.effective_user.id, as_namedtuple=True)
    if not packs:
        update.message.reply_text(s.LIST_NO_PACKS)
        return

    packs = packs[:100]  # can't include more than 100 entities
    strings_list = ['<a href="{}">{}</a>'.format(utils.name2link(pack.name), pack.title) for pack in packs]
    update.message.reply_html('• {}'.format('\n• '.join(strings_list)))


stickersbot.add_handler(CommandHandler(['list', 'l'], on_list_command))
