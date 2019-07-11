import logging
import re

from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.error import BadRequest
from telegram.error import TelegramError
from telegram import ChatAction

from bot.overrides import Filters
from bot import strings as s
from bot import u
from bot import db
from bot import StickerFile

logger = logging.getLogger(__name__)


@u.action(ChatAction.TYPING)
@u.restricted
@u.failwithmessage
def on_create_command(bot, update, user_data):
    logger.info('%d: /create', update.effective_user.id)

    update.message.reply_text(s.PACK_CREATION_WAITING_TITLE)
    user_data['status'] = 'waiting_pack_title'


@u.action(ChatAction.TYPING)
@u.failwithmessage
def on_pack_title_receive(bot, update, user_data):
    logger.info('%d: received possible pack title', update.effective_user.id)

    if len(update.message.text) > 64:
        logger.info('pack title too long: %s', update.message.text)
        update.message.reply_text(s.PACK_TITLE_TOO_LONG)
        # do not change the user status and let him send another title
        return

    if '\n' in update.message.text:
        logger.info('pack title contains newline character')
        update.message.reply_text(s.PACK_TITLE_CONTAINS_NEWLINES)
        # do not change the user status and let him send another title
        return

    logger.info('pack title is valid')

    user_data['pack'] = dict(title=update.message.text)

    max_name_len = 64 - (len(bot.username) + 4)  # = max len - "_by_botusername", final string always added by the API

    user_data['status'] = 'waiting_pack_name'

    text = s.PACK_CREATION_WAITING_NAME.format(update.message.text, max_name_len)
    update.message.reply_html(text)


@u.action(ChatAction.TYPING)
@u.failwithmessage
def on_pack_name_receive(bot, update, user_data):
    logger.info('%d: received possible pack name (link)', update.effective_user.id)

    candidate_name = update.message.text
    max_name_len = 64 - (len(bot.username) + 4)
    if len(candidate_name) > max_name_len:
        logger.info('pack name too long (%d/%d)', len(candidate_name), max_name_len)
        update.message.reply_text(s.PACK_NAME_TOO_LONG.format(len(update.message.text), max_name_len))
        # do not change the user status and let him send another name
        return

    if not re.search(r'[a-z](?!__)\w+', candidate_name, re.IGNORECASE):
        logger.info('pack name not valid: %s', update.message.text)
        update.message.reply_html(s.PACK_NAME_INVALID)
        # do not change the user status and let him send another name
        return

    if db.check_for_name_duplicates(update.effective_user.id, candidate_name):
        logger.info('pack name already saved: %s', candidate_name)
        update.message.reply_text(s.PACK_NAME_DUPLICATE)
        # do not change the user status and let him send another name
        return

    logger.info('valid pack name: %s', candidate_name)

    user_data['pack']['name'] = candidate_name
    user_data['status'] = 'waiting_pack_first_sticker'

    update.message.reply_text(s.PACK_CREATION_WAITING_FIRST_STICKER)


@u.action(ChatAction.TYPING)
@u.failwithmessage
def on_first_sticker_receive(bot, update, user_data):
    logger.info('%d: first sticker of the pack received', update.effective_user.id)

    title, name = user_data['pack'].get('title', None), user_data['pack'].get('name', None)
    if not title or not name:
        logger.error('pack title or name missing (title: %s, name: %s)', title, name)
        update.message.reply_text(s.PACK_CREATION_FIRST_STICKER_PACK_DATA_MISSING)

        user_data.pop('pack', None)  # remove temp info
        user_data['status'] = ''  # reset user status

        return

    full_name = name + '_by_' + bot.username

    sticker = StickerFile(update.message.sticker or update.message.document, caption=update.message.caption)
    sticker.download(prepare_png=True)

    try:
        logger.debug('executing API request...')
        bot.create_new_sticker_set(
            user_id=update.effective_user.id,
            title=title,
            name=full_name,
            emojis=sticker.emoji,
            png_sticker=sticker.png_bytes_object
        )
    except (BadRequest, TelegramError) as e:
        logger.error('Telegram error while creating stickers pack: %s', e.message)
        error_code = u.get_exception_code(e.message)

        if error_code == 10:  # there's already a pack with that link
            update.message.reply_html(s.PACK_CREATION_ERROR_DUPLICATE_NAME.format(u.name2link(full_name)))
            user_data['pack'].pop('name', None)  # remove pack name
            user_data['status'] = 'waiting_pack_name'
        elif error_code == 13:
            update.message.reply_text(s.PACK_CREATION_ERROR_INVALID_NAME)
            user_data['pack'].pop('name', None)  # remove pack name
            user_data['status'] = 'waiting_pack_name'
        else:
            update.message.reply_html(s.PACK_CREATION_ERROR_GENERIC.format(e.message))

        return  # do not continue

    db.save_pack(update.effective_user.id, full_name, title)
    pack_link = u.name2link(full_name)
    update.message.reply_html(s.PACK_CREATION_PACK_CREATED.format(pack_link))

    sticker.delete()  # remove sticker files

    user_data['status'] = 'adding_stickers'  # wait for other stickers
    user_data['pack']['name'] = full_name
    # do not remove temporary data (user_data['pack']) because we are still adding stickers


HANDLERS = (
    CommandHandler(['create', 'new', 'n'], on_create_command, filters=Filters.status(''), pass_user_data=True),
    MessageHandler(Filters.status('waiting_pack_title'), on_pack_title_receive, pass_user_data=True),
    MessageHandler(Filters.status('waiting_pack_name'), on_pack_name_receive, pass_user_data=True),
    MessageHandler((Filters.sticker | Filters.png) & Filters.status('waiting_pack_first_sticker'),
                   on_first_sticker_receive, pass_user_data=True)
)
