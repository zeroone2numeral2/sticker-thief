import logging

from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram import ChatAction

from bot.overrides import Filters
from bot import strings as s
from bot import u
from bot import StickerFile

logger = logging.getLogger(__name__)


@u.action(ChatAction.TYPING)
@u.restricted
@u.failwithmessage
def on_remove_command(bot, update, user_data):
    logger.info('%d: /remove', update.effective_user.id)

    update.message.reply_text(s.REMOVE_STICKER_SELECT_STICKER)
    user_data['status'] = 'removing_stickers'


@u.action(ChatAction.TYPING)
@u.failwithmessage
def on_sticker_receive(bot, update, user_data):
    logger.info('%d: user sent the stciker to add', update.effective_user.id)

    sticker = StickerFile(update.message.sticker)

    error = sticker.remove_from_set(bot)
    pack_link = u.name2link(update.message.sticker.set_name)
    if not error:
        update.message.reply_html(s.REMOVE_STICKER_SUCCESS.format(pack_link), quote=True)
    elif error == 11:
        update.message.reply_html(s.REMOVE_STICKER_FOREIGN_PACK.format(u.name2link(update.message.sticker.set_name)),
                                  quote=True)
    elif error == 12:
        update.message.reply_html(s.REMOVE_STICKER_ALREADY_DELETED.format(pack_link), quote=True)
    else:
        update.message.reply_html(s.REMOVE_STICKER_GENERIC_ERROR.format(pack_link, error), quote=True)


HANDLERS = (
    CommandHandler(['remove', 'rem', 'r'], on_remove_command, filters=Filters.status(''), pass_user_data=True),
    MessageHandler(Filters.sticker & Filters.status('removing_stickers'), on_sticker_receive, pass_user_data=True)
)
