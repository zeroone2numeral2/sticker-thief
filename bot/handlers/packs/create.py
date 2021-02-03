import logging
import re

# noinspection PyPackageRequirements
from telegram.error import BadRequest
from telegram.ext import (
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler
)
# noinspection PyPackageRequirements
from telegram import ChatAction, Update

from bot import stickersbot
from bot.strings import Strings
from bot.database.base import session_scope
from bot.database.models.pack import Pack
from bot.markups import InlineKeyboard
from bot.sticker import StickerFile
import bot.sticker.error as error
from ..conversation_statuses import Status
from ...utils import decorators
from ...utils import utils

logger = logging.getLogger(__name__)


@decorators.action(ChatAction.TYPING)
@decorators.restricted
@decorators.failwithmessage
@decorators.logconversation
def on_create_static_pack_command(update: Update, context: CallbackContext):
    logger.info('/create')

    context.user_data['pack'] = dict(animated=False)

    update.message.reply_html(
        Strings.PACK_CREATION_WAITING_TITLE,
        reply_markup=InlineKeyboard.static_animated_switch()
    )
    
    return Status.CREATE_WAITING_TITLE


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
@decorators.logconversation
def on_pack_title_receive(update: Update, context: CallbackContext):
    logger.info('received possible pack title')

    if len(update.message.text) > 64:
        logger.info('pack title too long: %s', update.message.text)
        update.message.reply_text(Strings.PACK_TITLE_TOO_LONG)
        # do not change the user status and let him send another title
        return Status.CREATE_WAITING_TITLE

    if '\n' in update.message.text:
        logger.info('pack title contains newline character')
        update.message.reply_text(Strings.PACK_TITLE_CONTAINS_NEWLINES)
        # do not change the user status and let him send another title
        return Status.CREATE_WAITING_TITLE

    logger.info('pack title is valid')

    context.user_data['pack']['title'] = update.message.text

    # max len of a pack name = 64 - "_by_botusername", final string always added by the API
    max_name_len = 64 - (len(context.bot.username) + 4)

    text = Strings.PACK_CREATION_WAITING_NAME.format(update.message.text, max_name_len)
    update.message.reply_html(text)
    
    return Status.CREATE_WAITING_NAME


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
@decorators.logconversation
def on_pack_name_receive(update: Update, context: CallbackContext):
    logger.info('received possible pack name (link)')
    logger.debug('user_data: %s', context.user_data)

    candidate_name = update.message.text
    max_name_len = 64 - (len(context.bot.username) + 4)
    if len(candidate_name) > max_name_len:
        logger.info('pack name too long (%d/%d)', len(candidate_name), max_name_len)
        update.message.reply_text(Strings.PACK_NAME_TOO_LONG.format(len(update.message.text), max_name_len))
        # do not change the user status and let him send another name
        return Status.CREATE_WAITING_NAME

    if not re.search(r'^[a-z](?!__)\w+$', candidate_name, re.IGNORECASE):
        logger.info('pack name not valid: %s', update.message.text)
        update.message.reply_html(Strings.PACK_NAME_INVALID)
        # do not change the user status and let him send another name
        return Status.CREATE_WAITING_NAME

    name_already_used = False
    with session_scope() as session:
        # https://stackoverflow.com/a/34112760
        if session.query(Pack).filter(Pack.user_id==update.effective_user.id, Pack.name==candidate_name).first() is not None:
            logger.info('pack name already saved: %s', candidate_name)
            name_already_used = True

    if name_already_used:
        update.message.reply_text(Strings.PACK_NAME_DUPLICATE)
        # do not change the user status and let him send another name
        return Status.CREATE_WAITING_NAME

    logger.info('valid pack name: %s', candidate_name)

    context.user_data['pack']['name'] = candidate_name

    if context.user_data['pack']['animated']:
        text = Strings.PACK_CREATION_WAITING_FIRST_ANIMATED_STICKER
    else:
        text = Strings.PACK_CREATION_WAITING_FIRST_STATIC_STICKER

    update.message.reply_text(text)

    return Status.CREATE_WAITING_FIRST_STICKER


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
@decorators.logconversation
def on_bad_first_static_sticker_receive(update: Update, _):
    logger.info('user sent an animated sticker instead of a static one')

    update.message.reply_text(Strings.ADD_STICKER_EXPECTING_STATIC)

    return Status.CREATE_WAITING_FIRST_STICKER


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
@decorators.logconversation
def on_first_sticker_receive(update: Update, context: CallbackContext):
    logger.info('first sticker of the pack received')
    logger.debug('user_data: %s', context.user_data)

    animated_pack = context.user_data['pack']['animated']
    if update.message.document:
        animated_sticker = False
    else:
        animated_sticker = update.message.sticker.is_animated

    if animated_pack and not animated_sticker:
        logger.info('invalid sticker: static sticker for an animated pack')
        update.message.reply_text(Strings.ADD_STICKER_EXPECTING_ANIMATED)
        return Status.CREATE_WAITING_FIRST_STICKER
    elif not animated_pack and animated_sticker:
        logger.info('invalid sticker: animated sticker for a static pack')
        update.message.reply_text(Strings.ADD_STICKER_EXPECTING_STATIC)
        return Status.CREATE_WAITING_FIRST_STICKER
    else:
        logger.info('sticker type ok (animated pack: %s, animated sticker: %s)', animated_pack, animated_sticker)

    title, name = context.user_data['pack'].get('title', None), context.user_data['pack'].get('name', None)
    if not title or not name:
        logger.error('pack title or name missing (title: %s, name: %s)', title, name)
        update.message.reply_text(Strings.PACK_CREATION_FIRST_STICKER_PACK_DATA_MISSING)

        context.user_data.pop('pack', None)  # remove temp info

        return ConversationHandler.END

    full_name = '{}_by_{}'.format(name, context.bot.username)

    user_emojis = context.user_data['pack'].pop('emojis', None)  # we also remove them
    sticker = StickerFile(
        bot=context.bot,
        message=update.message,
        emojis=user_emojis
    )
    sticker.download()

    try:
        logger.debug('executing API request...')
        request_payload = dict(
            user_id=update.effective_user.id,
            title=title,
            name=full_name,
            emojis=''.join(sticker.emojis),
        )

        sticker.create_set(**request_payload)
    except (error.PackInvalid, error.NameInvalid, error.NameAlreadyOccupied) as e:
        logger.error('Telegram error while creating stickers pack: %s', e.message)
        if isinstance(e, error.NameAlreadyOccupied):
            # there's already a pack with that link
            update.message.reply_html(Strings.PACK_CREATION_ERROR_DUPLICATE_NAME.format(utils.name2link(full_name)))
        elif isinstance(e, (error.PackInvalid, error.NameInvalid)):
            update.message.reply_text(Strings.PACK_CREATION_ERROR_INVALID_NAME)

        context.user_data['pack'].pop('name', None)  # remove pack name
        sticker.close()

        return Status.CREATE_WAITING_NAME  # do not continue, wait for another name
    except error.InvalidAnimatedSticker as e:
        logger.error('Telegram error while creating animated pack: %s', e.message)
        update.message.reply_html(Strings.ADD_STICKER_INVALID_ANIMATED, quote=True, disable_web_page_preview=True)

        return Status.CREATE_WAITING_FIRST_STICKER
    except error.FloodControlExceeded as e:
        logger.error('Telegram error while creating animated pack: %s', e.message)
        retry_in = re.search(r'retry in (\d+) seconds', e.message, re.I).group(1)  # Retry in 8 seconds
        text = Strings.ADD_STICKER_FLOOD_EXCEPTION.format(retry_in)

        update.message.reply_html(text, quote=True, disable_web_page_preview=True)

        return ConversationHandler.END  # do not continue, end the conversation
    except error.UnknwonError as e:
        logger.error('Unknown error while creating the pack: %s', e.message)
        update.message.reply_html(Strings.PACK_CREATION_ERROR_GENERIC.format(e.message))

        context.user_data.pop('pack', None)  # remove temp data
        sticker.close()

        return ConversationHandler.END  # do not continue, end the conversation
    else:
        # success

        pack_row = Pack(user_id=update.effective_user.id, name=full_name, title=title, is_animated=animated_pack)
        with session_scope() as session:
            session.add(pack_row)

        # db.save_pack(update.effective_user.id, full_name, title)
        pack_link = utils.name2link(full_name)
        update.message.reply_html(Strings.PACK_CREATION_PACK_CREATED.format(pack_link))

        sticker.close()  # remove sticker files

        context.user_data['pack']['name'] = full_name
        # do not remove temporary data (user_data['pack']) because we are still adding stickers

        # wait for other stickers
        if animated_pack:
            return Status.WAITING_ANIMATED_STICKERS
        else:
            return Status.WAITING_STATIC_STICKERS


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
@decorators.logconversation
def on_first_sticker_text_receive(update: Update, context: CallbackContext):
    logger.info('user sent a text message while we were waiting for the first sticker of a pack')
    logger.debug('user_data: %s', context.user_data)

    emojis = utils.get_emojis(update.message.text, as_list=True)
    if not emojis:
        update.message.reply_text(Strings.ADD_STICKER_NO_EMOJI_IN_TEXT)
        return Status.CREATE_WAITING_FIRST_STICKER
    elif len(emojis) > 10:
        update.message.reply_text(Strings.ADD_STICKER_TOO_MANY_EMOJIS)
        return Status.CREATE_WAITING_FIRST_STICKER

    context.user_data['pack']['emojis'] = emojis

    update.message.reply_text(Strings.ADD_STICKER_EMOJIS_SAVED.format(
        len(emojis),
        ''.join(emojis)
    ))

    return Status.CREATE_WAITING_FIRST_STICKER


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
@decorators.logconversation
def on_waiting_title_invalid_message(update: Update, _):
    logger.info('(create) waiting title: wrong type of message received')

    update.message.reply_html(Strings.PACK_TITLE_INVALID_MESSAGE)

    return Status.CREATE_WAITING_TITLE


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
@decorators.logconversation
def on_waiting_name_invalid_message(update: Update, _):
    logger.info('(create) waiting name: wrong type of message received')

    update.message.reply_html(Strings.PACK_NAME_INVALID_MESSAGE)

    return Status.CREATE_WAITING_NAME


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
@decorators.logconversation
def on_waiting_first_sticker_invalid_message(update: Update, _):
    logger.info('waiting first sticker: wrong type of message received')

    update.message.reply_html(Strings.PACK_CREATION_WAITING_FIRST_STICKER_INVALID_MESSAGE)

    return Status.CREATE_WAITING_FIRST_STICKER


@decorators.failwithmessage
def on_switch_pack_type(update: Update, context: CallbackContext):
    logger.info('swicth pack type inline keyboard')

    if not context.user_data.get('pack', None):
        update.callback_query.answer(Strings.PACK_TYPE_BUTTONS_EXPIRED)
        update.callback_query.message.edit_reply_markup(reply_markup=InlineKeyboard.REMOVE)
        return

    match = context.matches[0].group(1)
    reply_markup = InlineKeyboard.static_animated_switch(animated=match == 'animated')

    if match == 'animated':
        context.user_data['pack']['animated'] = True
    else:
        context.user_data['pack']['animated'] = False

    try:
        update.callback_query.message.edit_reply_markup(reply_markup=reply_markup)
    except BadRequest:
        pass

    update.callback_query.answer(Strings.PACK_TYPE_CHANGED.format(match))


stickersbot.add_handler(CallbackQueryHandler(on_switch_pack_type, pattern='packtype:(.+)'))

