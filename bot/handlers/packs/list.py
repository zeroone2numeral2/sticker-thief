import logging

# noinspection PyPackageRequirements
from telegram.ext import CommandHandler
# noinspection PyPackageRequirements
from telegram import ChatAction, Update

from bot import stickersbot
from bot.utils import decorators
from bot.utils import utils
from bot.database.base import session_scope
from bot.database.models.pack import Pack
from bot.strings import Strings

logger = logging.getLogger(__name__)


@decorators.action(ChatAction.TYPING)
@decorators.restricted
@decorators.failwithmessage
def on_list_command(update: Update, _):
    logger.info('/list')

    # packs = db.get_user_packs(update.effective_user.id, as_namedtuple=True)
    with session_scope() as session:
        packs = session.query(Pack).filter_by(user_id=update.effective_user.id).all()
        packs = packs[:100]  # can't include more than 100 entities
        strings_list = ['<a href="{}">{}</a>'.format(utils.name2link(pack.name), pack.title) for pack in packs]

    if not strings_list:
        update.message.reply_text(Strings.LIST_NO_PACKS)
        return

    update.message.reply_html('• {}'.format('\n• '.join(strings_list)))


stickersbot.add_handler(CommandHandler(['list', 'l'], on_list_command))
