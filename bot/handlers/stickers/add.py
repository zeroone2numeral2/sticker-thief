import logging
import re

# noinspection PyPackageRequirements
from telegram.ext import (
    ConversationHandler,
    CallbackContext
)
# noinspection PyPackageRequirements
from telegram import ChatAction, Update

from bot.strings import Strings
from bot.database.base import session_scope
from bot.database.models.pack import Pack
from bot.markups import Keyboard
from bot.sticker import StickerFile
import bot.sticker.error as error
from ..conversation_statuses import Status
from ...utils import decorators
from ...utils import utils

logger = logging.getLogger(__name__)

MAX_PACK_SIZE_STATIC = 120
MAX_PACK_SIZE_ANIMATED = 50


@decorators.action(ChatAction.TYPING)
@decorators.restricted
@decorators.failwithmessage
@decorators.logconversation
def on_add_command(update: Update, _):
    logger.info('/add')

    user_id = update.effective_user.id

    with session_scope() as session:
        pack_titles = [t.title for t in session.query(Pack.title).filter_by(user_id=user_id).order_by(Pack.title).all()]

    if not pack_titles:
        update.message.reply_text(Strings.ADD_STICKER_NO_PACKS)

        return ConversationHandler.END
    else:
        markup = Keyboard.from_list(pack_titles)
        update.message.reply_text(Strings.ADD_STICKER_SELECT_PACK, reply_markup=markup)

        return Status.ADD_WAITING_TITLE


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
@decorators.logconversation
def on_pack_title(update: Update, context: CallbackContext):
    logger.info('user selected the pack title from the keyboard')

    selected_title = update.message.text
    user_id = update.effective_user.id

    with session_scope() as session:
        packs_by_title = session.query(Pack).filter_by(title=selected_title, user_id=user_id).order_by(Pack.name).all()

        # for some reason, accessing a Pack attribute outside of a session
        # raises an error: https://docs.sqlalchemy.org/en/13/errors.html#object-relational-mapping
        # so we preload the list here in case we're going to need it later, to avoid a more complex handling
        # of the session
        by_bot_part = '_by_' + context.bot.username
        pack_names = [pack.name.replace(by_bot_part, '', 1) for pack in packs_by_title]  # strip the '_by_bot' part
        pack_animated = packs_by_title[0].is_animated  # we need this in case there's only one pack and we need to know whether it is animated or not

    if not packs_by_title:
        logger.error('cannot find any pack with this title: %s', selected_title)
        update.message.reply_text(Strings.ADD_STICKER_SELECTED_TITLE_DOESNT_EXIST.format(selected_title[:150]))
        # do not change the user status
        return Status.ADD_WAITING_TITLE

    if len(packs_by_title) > 1:
        logger.info('user has multiple packs with this title: %s', selected_title)

        markup = Keyboard.from_list(pack_names, add_back_button=True)

        # list with the links to the involved packs
        pack_links = ['<a href="{}">{}</a>'.format(utils.name2link(pack_name, bot_username=context.bot.username), pack_name) for pack_name in pack_names]
        text = Strings.ADD_STICKER_SELECTED_TITLE_MULTIPLE.format(selected_title, '\n• '.join(pack_links))
        update.message.reply_html(text, reply_markup=markup)

        return Status.ADD_WAITING_NAME  # we now have to wait for the user to tap on a pack name

    logger.info('there is only one pack with the selected title (animated: %s), proceeding...', pack_animated)
    pack_name = '{}_by_{}'.format(pack_names[0], context.bot.username)

    context.user_data['pack'] = dict(name=pack_name, animated=pack_animated)
    pack_link = utils.name2link(pack_name)
    base_string = Strings.ADD_STICKER_PACK_SELECTED_STATIC if not pack_animated else Strings.ADD_STICKER_PACK_SELECTED_ANIMATED
    update.message.reply_html(base_string.format(pack_link), reply_markup=Keyboard.HIDE)

    if pack_animated:
        return Status.WAITING_ANIMATED_STICKERS
    else:
        return Status.WAITING_STATIC_STICKERS


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
@decorators.logconversation
def on_pack_name(update: Update, context: CallbackContext):
    logger.info('user selected the pack name from the keyboard')
    logger.debug('user_data: %s', context.user_data)

    if re.search(r'^GO BACK$', update.message.text, re.I):
        with session_scope() as session:
            pack_titles = [t.title for t in session.query(Pack.title).filter_by(user_id=update.effective_user.id).all()]

        markup = Keyboard.from_list(pack_titles)
        update.message.reply_text(Strings.ADD_STICKER_SELECT_PACK, reply_markup=markup)

        return Status.ADD_WAITING_TITLE

    # the buttons list has the name without "_by_botusername"
    selected_name = '{}_by_{}'.format(update.message.text, context.bot.username)

    with session_scope() as session:
        pack = session.query(Pack).filter_by(name=selected_name, user_id=update.effective_user.id).first()
        pack_name = pack.name
        pack_animated = pack.is_animated

    if not pack_name:
        logger.error('user %d does not have any pack with name %s', update.effective_user.id, selected_name)
        update.message.reply_text(Strings.ADD_STICKER_SELECTED_NAME_DOESNT_EXIST)
        # do not reset the user status
        return Status.ADD_WAITING_NAME

    logger.info('selected pack is animated: %s', pack_animated)

    context.user_data['pack'] = dict(name=pack_name, animated=pack_animated)
    pack_link = utils.name2link(pack_name)
    base_string = Strings.ADD_STICKER_PACK_SELECTED_STATIC if not pack_animated else Strings.ADD_STICKER_PACK_SELECTED_ANIMATED
    update.message.reply_html(base_string.format(pack_link), reply_markup=Keyboard.HIDE)

    if pack_animated:
        return Status.WAITING_ANIMATED_STICKERS
    else:
        return Status.WAITING_STATIC_STICKERS


def add_sticker_to_set(update: Update, context: CallbackContext, animated_pack):
    name = context.user_data['pack'].get('name', None)
    if not name:
        logger.error('pack name missing (%s)', name)
        update.message.reply_text(Strings.ADD_STICKER_PACK_DATA_MISSING)

        context.user_data.pop('pack', None)  # remove temp info

        return ConversationHandler.END

    user_emojis = context.user_data['pack'].pop('emojis', None)  # we also remove them
    sticker = StickerFile(bot=context.bot, message=update.message, emojis=user_emojis)
    sticker.download()

    pack_link = utils.name2link(name)

    # we edit this flag so the 'finally' statement can end the conversation if needed by an 'except'
    end_conversation = False
    try:
        logger.debug('executing request...')
        sticker.add_to_set(name)
    except error.PackFull:
        max_pack_size = MAX_PACK_SIZE_ANIMATED if animated_pack else MAX_PACK_SIZE_STATIC
        update.message.reply_html(Strings.ADD_STICKER_PACK_FULL.format(pack_link, max_pack_size), quote=True)

        end_conversation = True  # end the conversation when a pack is full
    except error.FileDimensionInvalid:
        logger.error('resized sticker has the wrong size: %s', str(sticker))
        update.message.reply_html(Strings.ADD_STICKER_SIZE_ERROR.format(*sticker.size), quote=True)
    except error.InvalidAnimatedSticker:
        update.message.reply_html(Strings.ADD_STICKER_INVALID_ANIMATED, quote=True, disable_web_page_preview=True)
    except error.PackInvalid:
        # pack name invalid or that pack has been deleted: delete it from the db
        with session_scope() as session:
            deleted_rows = session.query(Pack).filter(Pack.user_id == update.effective_user.id,
                                                      Pack.name == name).delete('fetch')
            logger.debug('rows deleted: %d', deleted_rows or 0)

            # get the remaining packs' titles
            pack_titles = [t.title for t in session.query(Pack.title).filter_by(user_id=update.effective_user.id).order_by(Pack.title).all()]

        if not pack_titles:
            # user doesn't have any other pack to chose from, reset his status
            update.message.reply_html(Strings.ADD_STICKER_PACK_NOT_VALID_NO_PACKS.format(pack_link))

            logger.debug('calling sticker.delete()...')
            sticker.close()
            return ConversationHandler.END
        else:
            # make the user select another pack from the keyboard
            markup = Keyboard.from_list(pack_titles)
            update.message.reply_html(Strings.ADD_STICKER_PACK_NOT_VALID.format(pack_link), reply_markup=markup)
            context.user_data['pack'].pop('name', None)  # remove temporary data

            logger.debug('calling sticker.delete()...')
            sticker.close()
            return Status.ADD_WAITING_TITLE
    except error.UnknwonError as e:
        update.message.reply_html(Strings.ADD_STICKER_GENERIC_ERROR.format(pack_link, e.message), quote=True)
    except Exception as e:
        logger.error('non-telegram exception while adding a sticker to a set', exc_info=True)
        raise e  # this is not raised
    else:
        if not user_emojis:
            text = Strings.ADD_STICKER_SUCCESS.format(pack_link)
        else:
            text = Strings.ADD_STICKER_SUCCESS_USER_EMOJIS.format(pack_link, ''.join(user_emojis))

        update.message.reply_html(text, quote=True)
    finally:
        # this is entered even when we enter the 'else' or we return in an 'except'
        # https://stackoverflow.com/a/19805746
        logger.debug('calling sticker.close()...')
        sticker.close()

        if end_conversation:
            return ConversationHandler.END

        if animated_pack:
            return Status.WAITING_ANIMATED_STICKERS
        else:
            return Status.WAITING_STATIC_STICKERS


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
@decorators.logconversation
def on_static_sticker_receive(update: Update, context: CallbackContext):
    logger.info('user sent a static sticker to add')
    logger.debug('user_data: %s', context.user_data)

    return add_sticker_to_set(update, context, animated_pack=False)


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
@decorators.logconversation
def on_animated_sticker_receive(update: Update, context: CallbackContext):
    logger.info('user sent an animated sticker to add')
    logger.debug('user_data: %s', context.user_data)

    return add_sticker_to_set(update, context, animated_pack=True)


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
@decorators.logconversation
def on_bad_static_sticker_receive(update: Update, _):
    logger.info('user sent an animated sticker instead of a static one')

    update.message.reply_text(Strings.ADD_STICKER_EXPECTING_STATIC)

    return Status.WAITING_STATIC_STICKERS


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
@decorators.logconversation
def on_bad_animated_sticker_receive(update: Update, _):
    logger.info('user sent a static sticker instead of an animated one')

    update.message.reply_text(Strings.ADD_STICKER_EXPECTING_ANIMATED)

    return Status.WAITING_ANIMATED_STICKERS


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
@decorators.logconversation
def on_text_receive(update: Update, context: CallbackContext):
    logger.info('user sent a text message while we were waiting for a sticker')
    logger.debug('user_data: %s', context.user_data)

    status_to_return = Status.WAITING_STATIC_STICKERS
    if context.user_data['pack']['animated']:
        status_to_return = Status.WAITING_ANIMATED_STICKERS

    emojis = utils.get_emojis(update.message.text, as_list=True)
    if not emojis:
        update.message.reply_text(Strings.ADD_STICKER_NO_EMOJI_IN_TEXT)
        return status_to_return
    elif len(emojis) > 10:
        update.message.reply_text(Strings.ADD_STICKER_TOO_MANY_EMOJIS)
        return status_to_return

    context.user_data['pack']['emojis'] = emojis

    update.message.reply_text(Strings.ADD_STICKER_EMOJIS_SAVED.format(
        len(emojis),
        ''.join(emojis)
    ))

    return status_to_return


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
@decorators.logconversation
def on_waiting_title_invalid_message(update: Update, _):
    logger.info('(add) waiting title: wrong type of message received')

    update.message.reply_html(Strings.PACK_TITLE_INVALID_MESSAGE)

    return Status.ADD_WAITING_TITLE


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
@decorators.logconversation
def on_waiting_name_invalid_message(update: Update, _):
    logger.info('(add) waiting name: wrong type of message received')

    update.message.reply_html(Strings.PACK_NAME_INVALID_MESSAGE)

    return Status.ADD_WAITING_NAME


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
@decorators.logconversation
def on_waiting_sticker_invalid_message(update: Update, context: CallbackContext):
    logger.info('(add) waiting sticker: wrong type of message received')

    status_to_return = Status.WAITING_STATIC_STICKERS
    if context.user_data['pack']['animated']:
        status_to_return = Status.WAITING_ANIMATED_STICKERS

    update.message.reply_html(Strings.ADD_STICKER_INVALID_MESSAGE)

    return status_to_return

