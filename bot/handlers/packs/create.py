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

from bot import stickersbot
from bot.strings import Strings
from bot.database.base import session_scope
from bot.database.models.pack import Pack
from bot.sticker import StickerFile
import bot.sticker.error as error
from ..fallback_commands import cancel_command
from ..stickers.add import on_sticker_receive
from ...customfilters import CustomFilters
from ...utils import decorators
from ...utils import utils

logger = logging.getLogger(__name__)


WAITING_TITLE, WAITING_NAME, WAITING_FIRST_STICKER, WAITING_FIRST_ANIMATED_STICKER, ADDING_STICKERS, ADDING_ANIMATED_STICKERS = range(6)


@decorators.action(ChatAction.TYPING)
@decorators.restricted
@decorators.failwithmessage
def on_create_command(update: Update, context: CallbackContext):
    logger.info('/create')

    context.user_data['pack'] = dict(animated=False)

    update.message.reply_text(Strings.PACK_CREATION_WAITING_TITLE)
    
    return WAITING_TITLE


@decorators.action(ChatAction.TYPING)
@decorators.restricted
@decorators.failwithmessage
def on_create_animated_command(update: Update, context: CallbackContext):
    logger.info('/createanimated')

    context.user_data['pack'] = dict(animated=True)

    update.message.reply_text(Strings.PACK_CREATION_WAITING_TITLE)

    return WAITING_TITLE


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
def on_pack_title_receive(update: Update, context: CallbackContext):
    logger.info('received possible pack title')

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

    context.user_data['pack']['title'] = update.message.text

    # max len of a pack name = 64 - "_by_botusername", final string always added by the API
    max_name_len = 64 - (len(context.bot.username) + 4)

    text = Strings.PACK_CREATION_WAITING_NAME.format(update.message.text, max_name_len)
    update.message.reply_html(text)
    
    return WAITING_NAME


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
def on_pack_name_receive(update: Update, context: CallbackContext):
    logger.info('received possible pack name (link)')
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

    name_already_used = False
    with session_scope() as session:
        # https://stackoverflow.com/a/34112760
        if session.query(Pack).filter(Pack.user_id==update.effective_user.id, Pack.name==candidate_name).first() is not None:
            logger.info('pack name already saved: %s', candidate_name)
            name_already_used = True

    if name_already_used:
        update.message.reply_text(Strings.PACK_NAME_DUPLICATE)
        # do not change the user status and let him send another name
        return WAITING_NAME

    logger.info('valid pack name: %s', candidate_name)

    context.user_data['pack']['name'] = candidate_name

    update.message.reply_text(Strings.PACK_CREATION_WAITING_FIRST_STICKER)

    if context.user_data['pack']['animated']:
        return WAITING_FIRST_ANIMATED_STICKER
    else:
        return WAITING_FIRST_STICKER


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
def on_bad_first_sticker_receive(update: Update, _):
    logger.info('user sent an animated sticker instead of a static one')

    update.message.reply_text(Strings.ADD_STICKER_EXPECTING_STATIC)

    return WAITING_FIRST_STICKER


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
def on_bad_first_animated_sticker_receive(update: Update, _):
    logger.info('user sent a static animated sticker instead of an animated one')

    update.message.reply_text(Strings.ADD_STICKER_EXPECTING_ANIMATED)

    return WAITING_FIRST_ANIMATED_STICKER


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
def on_first_sticker_receive(update: Update, context: CallbackContext):
    logger.info('first sticker of the static pack received')
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
        StickerFile.create_set(
            bot=context.bot,
            user_id=update.effective_user.id,
            title=title,
            name=full_name,
            emojis=sticker.emoji,
            # we need to use an input file becase a tempfile.SpooledTemporaryFile has a 'name' attribute which
            # makes python-telegram-bot retrieve the file's path using os (https://github.com/python-telegram-bot/python-telegram-bot/blob/2a3169a22f7227834dd05a35f90306375136e41a/telegram/files/inputfile.py#L58)
            #  to populate the 'filename' attribute, which would result an exception since it is
            #  a byte object. That means we have to do it ourself by  creating the InputFile and
            #  assigning it a custom 'filename'
            png_sticker=sticker.png_input_file
        )
    except (error.PackInvalid, error.NameInvalid, error.NameAlreadyOccupied) as e:
        logger.error('Telegram error while creating stickers pack: %s', e.message)
        if isinstance(e, error.NameAlreadyOccupied):
            # there's already a pack with that link
            update.message.reply_html(Strings.PACK_CREATION_ERROR_DUPLICATE_NAME.format(utils.name2link(full_name)))
        elif isinstance(e, (error.PackInvalid, error.NameInvalid)):
            update.message.reply_text(Strings.PACK_CREATION_ERROR_INVALID_NAME)

        context.user_data['pack'].pop('name', None)  # remove pack name
        sticker.close()

        return WAITING_NAME  # do not continue, wait for another name
    except error.UnknwonError as e:
        logger.error('Unknown error while creating the pack: %s', e.message)
        update.message.reply_html(Strings.PACK_CREATION_ERROR_GENERIC.format(e.message))

        context.user_data.pop('pack', None)  # remove temp data
        sticker.close()

        return ConversationHandler.END  # do not continue, end the conversation
    else:
        # success

        pack_row = Pack(user_id=update.effective_user.id, name=full_name, title=title)
        with session_scope() as session:
            session.add(pack_row)

        # db.save_pack(update.effective_user.id, full_name, title)
        pack_link = utils.name2link(full_name)
        update.message.reply_html(Strings.PACK_CREATION_PACK_CREATED.format(pack_link))

        sticker.close()  # remove sticker files

        context.user_data['pack']['name'] = full_name
        # do not remove temporary data (user_data['pack']) because we are still adding stickers

        return ADDING_STICKERS  # wait for other stickers


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
def on_first_animated_sticker_receive(update: Update, context: CallbackContext):
    logger.info('first sticker of the animated pack received')

    raise NotImplementedError


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
def on_animated_sticker_receive(update: Update, context: CallbackContext):
    logger.info('animated sticker to add to the animated pack received')

    raise NotImplementedError


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
def on_bad_sticker_receive(update: Update, _):
    logger.info('user sent an animated sticker instead of a static one')

    update.message.reply_text(Strings.ADD_STICKER_EXPECTING_STATIC)

    return ADDING_STICKERS


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
def on_bad_animated_sticker_receive(update: Update, _):
    logger.info('user sent a static sticker instead of an animated one')

    update.message.reply_text(Strings.ADD_STICKER_EXPECTING_ANIMATED)

    return ADDING_ANIMATED_STICKERS


stickersbot.add_handler(ConversationHandler(
    name='pack_creation',
    entry_points=[
        CommandHandler(['create', 'new', 'n'], on_create_command),
        CommandHandler(['createanimated', 'newanimated', 'na'], on_create_animated_command)
    ],
    states={
        WAITING_TITLE: [MessageHandler(Filters.text, on_pack_title_receive)],
        WAITING_NAME: [MessageHandler(Filters.text, on_pack_name_receive)],
        WAITING_FIRST_STICKER: [
            MessageHandler(
                CustomFilters.static_sticker | Filters.document.category('image/png'),
                on_first_sticker_receive
            ),
            MessageHandler(
                CustomFilters.animated_sticker,
                on_bad_first_sticker_receive  # we were expecting a static sticker, got an animated one instead
            ),
        ],
        WAITING_FIRST_ANIMATED_STICKER: [
            MessageHandler(CustomFilters.animated_sticker, on_first_animated_sticker_receive),
            MessageHandler(
                CustomFilters.static_sticker | Filters.document.category('image/png'),
                on_bad_first_animated_sticker_receive  # we were expecting an animated sticker, got a static one instead
            ),
        ],
        ADDING_STICKERS: [
            MessageHandler(
                CustomFilters.static_sticker | Filters.document.category('image/png'),
                on_sticker_receive
            ),
            MessageHandler(CustomFilters.animated_sticker, on_bad_sticker_receive),
        ],
        ADDING_ANIMATED_STICKERS: [
            MessageHandler(CustomFilters.animated_sticker, on_animated_sticker_receive),
            MessageHandler(
                CustomFilters.static_sticker | Filters.document.category('image/png'),
                on_bad_animated_sticker_receive
            ),
        ]
    },
    fallbacks=[CommandHandler(['cancel', 'c', 'done', 'd'], cancel_command)]
))
