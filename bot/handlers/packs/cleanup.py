import logging

# noinspection PyPackageRequirements
from telegram.ext import CommandHandler, CallbackContext
# noinspection PyPackageRequirements
from telegram import ChatAction, Update, TelegramError

from bot import stickersbot
from bot.utils import decorators
from bot.utils import utils
from bot.database.base import session_scope
from bot.database.models.pack import Pack
from bot.strings import Strings

logger = logging.getLogger(__name__)

RANDOM_FILE_ID = 'CAACAgQAAxkBAAEC2wdehE0E8h1kfSZwYUrP9Axz2tfH7AACW2UAAuOnXQVS1pXsJFAxLxgE'


@decorators.action(ChatAction.TYPING)
@decorators.restricted
@decorators.failwithmessage
def on_cleanup_command(update: Update, context: CallbackContext):
    logger.info('/cleanup')

    # packs = db.get_user_packs(update.effective_user.id, as_namedtuple=True)
    with session_scope() as session:
        packs = session.query(Pack).filter_by(user_id=update.effective_user.id).all()
        packs = [(p.title, p.name, p.is_animated) for p in packs]

    if not packs:
        update.message.reply_text(Strings.LIST_NO_PACKS)
        return

    packs_to_delete = list()
    for pack in packs:
        logger.debug('checking pack: %s', pack[1])

        request_payload = dict(
            user_id=update.effective_user.id,
            name=pack[1],
            emojis='🗑'
        )

        if pack[2]:
            # is animated
            request_payload['tgs_sticker'] = open('requirements.txt', 'rb')  # yeah, uhhh... we need this
        else:
            request_payload['png_sticker'] = open('requirements.txt', 'rb')

        try:
            context.bot.add_sticker_to_set(**request_payload)
        except TelegramError as telegram_error:
            # this only work because Telegram first check the validity of the pack name, and then
            # if we passed a correct png_sticker/tgs_sticker. Will they ever change this, this command will break
            # and we have to pass a correct png/tgs file (right know we pass requirements.txt as bytes object)
            if 'Stickerset_invalid' in telegram_error.message:
                logger.debug('this pack will be removed from the db (%s)', telegram_error.message)
                packs_to_delete.append(pack)  # list of packs we will have to delete
            else:
                logger.debug('api exception: %s', telegram_error.message)

    if not packs_to_delete:
        update.message.reply_text(Strings.CLEANUP_NO_PACK)
        return

    with session_scope() as session:
        for _, pack_name, _ in packs_to_delete:
            logger.info('deleting pack from db...')
            session.query(Pack).filter(Pack.user_id==update.effective_user.id, Pack.name==pack_name).delete()

        logger.info('done')

    packs_links = ['<a href="{}">{}</a>'.format(utils.name2link(pack[1]), pack[0]) for pack in packs_to_delete]

    update.message.reply_html(Strings.CLEANUP_HEADER + '• {}'.format('\n• '.join(packs_links)))


stickersbot.add_handler(CommandHandler(['cleanup', 'cu'], on_cleanup_command))
