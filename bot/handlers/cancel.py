import logging

from telegram.ext import CommandHandler
from telegram import ChatAction

from bot import markups as rm
from bot import strings as s
from bot import u

logger = logging.getLogger(__name__)

STATUSES_DICT = {
    '': 'no active status',
    'waiting_pack_title': 'waiting for pack title',
    'waiting_pack_name': 'waiting for pack name',
    'waiting_pack_first_sticker': 'waiting for the first sticker of the pack',
    'adding_stickers': 'waiting for stickers to add',
    'adding_waiting_pack_title': 'waiting for the pack title of the target pack so we can add stickers to it',
    'removing_stickers': 'waiting for the sticker to remove from its pack',
    'exporting_pack_waiting_sticker': 'waiting for a sticker from the pack to export',
    'unknown': 'unmapped status'
}


@u.action(ChatAction.TYPING)
@u.restricted
@u.failwithmessage
def on_cancel_command(bot, update, user_data):
    logger.info('%d: /cancel', update.effective_user.id)

    user_status = user_data.get('status', 'unknown')
    logger.info('resetting status for %d (previous: %s)', update.effective_user.id, user_status)

    # reset user status
    user_data['status'] = ''

    # remove temporary data
    user_data.pop('pack', None)

    update.message.reply_text(s.CANCEL, reply_markup=rm.HIDE)


@u.action(ChatAction.TYPING)
@u.restricted
@u.failwithmessage
def on_status_command(bot, update, user_data):
    logger.info('%d: /status', update.effective_user.id)

    user_status = user_data.get('status', 'unknown')
    user_status_desc = STATUSES_DICT.get(user_status, user_status)
    logger.info('status of %d: %s', update.effective_user.id, user_status)

    update.message.reply_text(user_status_desc)


HANDLERS = (
    CommandHandler(['cancel', 'c'], on_cancel_command, pass_user_data=True),
    CommandHandler(['status', 's'], on_status_command, pass_user_data=True)
)
