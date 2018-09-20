import logging

from telegram.ext import MessageHandler

SEP = '-' * 70

logger = logging.getLogger(__name__)


def set_user_info(bot, update, user_data):
    logger.info(SEP)

    user_status = user_data.get('status', '')

    logger.debug('%d: priority handler (status: %s)', update.effective_user.id, user_status)

    update.message.from_user.status = user_status


HANDLER = MessageHandler(None, set_user_info, pass_user_data=True)
