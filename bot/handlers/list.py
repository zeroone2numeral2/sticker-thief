import logging

from telegram.ext import CommandHandler
from telegram import ChatAction

from bot import strings as s
from bot import u
from bot import db

logger = logging.getLogger(__name__)


@u.action(ChatAction.TYPING)
@u.restricted
@u.failwithmessage
def on_list_command(bot, update):
    logger.info('%d: /list', update.effective_user.id)

    packs = db.get_user_packs(update.effective_user.id, as_namedtuple=True)
    if not packs:
        update.message.reply_text(s.LIST_NO_PACKS)
        return

    packs = packs[:100]  # can't include more than 100 entities
    strings_list = ['<a href="{}">{}</a>'.format(u.name2link(pack.name), pack.title) for pack in packs]
    update.message.reply_html('• {}'.format('\n• '.join(strings_list)))


HANDLERS = (
    CommandHandler(['list', 'l'], on_list_command),
)
