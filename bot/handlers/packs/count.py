import logging

# noinspection PyPackageRequirements
from telegram.ext import CommandHandler, CallbackContext, ConversationHandler, run_async
# noinspection PyPackageRequirements
from telegram import ChatAction, Update, TelegramError

from bot import stickersbot
from bot.utils import decorators
from bot.utils import utils
from bot.database.base import session_scope
from bot.database.models.pack import Pack
from bot.strings import Strings

logger = logging.getLogger(__name__)


@run_async
@decorators.action(ChatAction.TYPING)
@decorators.restricted
@decorators.failwithmessage
def on_count_command(update: Update, context: CallbackContext):
    logger.info('/count')

    with session_scope() as session:
        packs = session.query(Pack).filter_by(user_id=update.effective_user.id).order_by(Pack.title).all()
        packs = [(p.title, p.name, p.is_animated) for p in packs]

    if not packs:
        update.message.reply_text(Strings.LIST_NO_PACKS)
        return

    update.message.reply_html("Hold on, this might take some time...")

    results_list = []
    for pack in packs:
        logger.debug('checking pack: %s', pack[1])

        pack_result_dict = dict(title=pack[0], name=pack[1], result=None)

        try:
            sticker_set = context.bot.get_sticker_set(user_id=update.effective_user.id, name=pack[1])
            pack_result_dict['result'] = len(sticker_set.stickers)
        except TelegramError as telegram_error:
            logger.debug('api exception: %s', telegram_error.message)
            pack_result_dict['result'] = telegram_error.message

        results_list.append(pack_result_dict)

    strings_list = ['<a href="{}">{}</a>: {}'.format(utils.name2link(p['name']), p['title'], p['result']) for p in results_list]

    update.message.reply_html('• {}'.format('\n• '.join(strings_list)))


stickersbot.add_handler(CommandHandler(['count'], on_count_command))
