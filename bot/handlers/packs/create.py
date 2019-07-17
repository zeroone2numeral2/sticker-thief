import logging
import re

# noinspection PyPackageRequirements
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    Filters
)
# noinspection PyPackageRequirements
from telegram import ChatAction, Update
# noinspection PyPackageRequirements
from telegram.error import BadRequest, TelegramError

from bot import stickersbot
from bot.strings import Strings
from bot import db
from bot.stickers import StickerFile
from ..fallback_commands import cancel_command
from ..stickers.add import on_sticker_receive
from ...utils import decorators
from ...utils import utils

logger = logging.getLogger(__name__)


WAITING_TITLE, WAITING_NAME, WAITING_FIRST_STICKER, ADDING_STICKERS = range(4)


@decorators.action(ChatAction.TYPING)
@decorators.restricted
@decorators.failwithmessage
def on_create_command(update: Update, _):
    logger.info('%d: /create', update.effective_user.id)

    update.message.reply_text(Strings.PACK_CREATION_WAITING_TITLE)
    
    return WAITING_TITLE


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
def on_pack_title_receive(update: Update, context: CallbackContext):
    logger.info('%d: received possible pack title', update.effective_user.id)

    if len(update.message.text) > 64:
        logger.info('pack title too long: %s', update.message.text)
        update.message.reply_text(Strings.PACK_TITLE_TOO_LONG)
        # do not change the user status and let him send another title
        return WAITING_TITLE

    if '\n' in update.message.text:
        logger.info('pack title contains newline character')
        update.message.reply_text(Strings.PACK_TITLE_CONTAINS_NEWLINES)
        # do not change the user status and let him send another title
        return WAITING_TITLE

    logger.info('pack title is valid')

    context.user_data['pack'] = dict(title=update.message.text)

    max_name_len = 64 - (len(context.bot.username) + 4)  # = max len - "_by_botusername", final string always added by the API

    text = Strings.PACK_CREATION_WAITING_NAME.format(update.message.text, max_name_len)
    update.message.reply_html(text)
    
    return WAITING_NAME


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
def on_pack_name_receive(update: Update, context: CallbackContext):
    logger.info('%d: received possible pack name (link)', update.effective_user.id)
    logger.debug('user_data: %s', context.user_data)

    candidate_name = update.message.text
    max_name_len = 64 - (len(context.bot.username) + 4)
    if len(candidate_name) > max_name_len:
        logger.info('pack name too long (%d/%d)', len(candidate_name), max_name_len)
        update.message.reply_text(Strings.PACK_NAME_TOO_LONG.format(len(update.message.text), max_name_len))
        # do not change the user status and let him send another name
        return WAITING_NAME

    if not re.search(r'[a-z](?!__)\w+', candidate_name, re.IGNORECASE):
        logger.info('pack name not valid: %s', update.message.text)
        update.message.reply_html(Strings.PACK_NAME_INVALID)
        # do not change the user status and let him send another name
        return WAITING_NAME

    if db.check_for_name_duplicates(update.effective_user.id, candidate_name):
        logger.info('pack name already saved: %s', candidate_name)
        update.message.reply_text(Strings.PACK_NAME_DUPLICATE)
        # do not change the user status and let him send another name
        return WAITING_NAME

    logger.info('valid pack name: %s', candidate_name)

    context.user_data['pack']['name'] = candidate_name

    update.message.reply_text(Strings.PACK_CREATION_WAITING_FIRST_STICKER)

    return WAITING_FIRST_STICKER


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
def on_first_sticker_receive(update: Update, context: CallbackContext):
    logger.info('%d: first sticker of the pack received', update.effective_user.id)
    logger.debug('user_data: %s', context.user_data)

    title, name = context.user_data['pack'].get('title', None), context.user_data['pack'].get('name', None)
    if not title or not name:
        logger.error('pack title or name missing (title: %s, name: %s)', title, name)
        update.message.reply_text(Strings.PACK_CREATION_FIRST_STICKER_PACK_DATA_MISSING)

        context.user_data.pop('pack', None)  # remove temp info

        return ConversationHandler.END

    full_name = '{}_by_{}'.format(name, context.bot.username)

    sticker = StickerFile(update.message.sticker or update.message.document, caption=update.message.caption)
    sticker.download(prepare_png=True)

    try:
        logger.debug('executing API request...')
        context.bot.create_new_sticker_set(
            user_id=update.effective_user.id,
            title=title,
            name=full_name,
            emojis=sticker.emoji,
            png_sticker=sticker.png_bytes_object
        )
    except (BadRequest, TelegramError) as e:
        logger.error('Telegram error while creating stickers pack: %s', e.message)
        error_code = utils.get_exception_code(e.message)

        if error_code == 10:  # there's already a pack with that link
            update.message.reply_html(Strings.PACK_CREATION_ERROR_DUPLICATE_NAME.format(utils.name2link(full_name)))
            context.user_data['pack'].pop('name', None)  # remove pack name

            return WAITING_NAME
        elif error_code == 13:
            update.message.reply_text(Strings.PACK_CREATION_ERROR_INVALID_NAME)
            context.user_data['pack'].pop('name', None)  # remove pack name

            return WAITING_NAME
        else:
            update.message.reply_html(Strings.PACK_CREATION_ERROR_GENERIC.format(e.message))

            return ConversationHandler.END  # do not continue

    db.save_pack(update.effective_user.id, full_name, title)
    pack_link = utils.name2link(full_name)
    update.message.reply_html(Strings.PACK_CREATION_PACK_CREATED.format(pack_link))

    sticker.delete()  # remove sticker files

    context.user_data['pack']['name'] = full_name
    # do not remove temporary data (user_data['pack']) because we are still adding stickers

    return ADDING_STICKERS  # wait for other stickers


stickersbot.add_handler(ConversationHandler(
    name='pack_creation',
    entry_points=[CommandHandler(['create', 'new', 'n'], on_create_command)],
    states={
        WAITING_TITLE: [MessageHandler(Filters.text, on_pack_title_receive)],
        WAITING_NAME: [MessageHandler(Filters.text, on_pack_name_receive)],
        WAITING_FIRST_STICKER: [MessageHandler(
            Filters.sticker | Filters.document.category('image/png'),
            on_first_sticker_receive
        )],
        ADDING_STICKERS: [MessageHandler(
            Filters.sticker | Filters.document.category('image/png'),
            on_sticker_receive
        )]
    },
    fallbacks=[CommandHandler(['cancel', 'c', 'done', 'd'], cancel_command)]
))
