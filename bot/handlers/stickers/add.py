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
from bot.markups import Keyboard
from bot.sticker import StickerFile
import bot.sticker.error as error
from ..fallback_commands import cancel_command
from ...customfilters import CustomFilters
from ...utils import decorators
from ...utils import utils

logger = logging.getLogger(__name__)

WAITING_TITLE, WAITING_NAME, WAITING_STICKERS = range(3)


@decorators.action(ChatAction.TYPING)
@decorators.restricted
@decorators.failwithmessage
def on_add_command(update: Update, _):
    logger.info('%d: /add', update.effective_user.id)

    with session_scope() as session:
        pack_titles = [t.title for t in session.query(Pack.title).filter_by(user_id=update.effective_user.id).all()]

    if not pack_titles:
        update.message.reply_text(Strings.ADD_STICKER_NO_PACKS)

        return ConversationHandler.END
    else:
        markup = Keyboard.from_list(pack_titles)
        update.message.reply_text(Strings.ADD_STICKER_SELECT_PACK, reply_markup=markup)

        return WAITING_TITLE


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
def on_pack_title(update: Update, context: CallbackContext):
    logger.info('%d: user selected the pack title from the keyboard', update.effective_user.id)

    selected_title = update.message.text

    with session_scope() as session:
        packs_by_title = session.query(Pack).filter_by(title=selected_title).all()

        # for some reason, accessing a Pack attribute outside of a session
        # raises an error: https://docs.sqlalchemy.org/en/13/errors.html#object-relational-mapping
        # so we preload the list here in case we're going to need it later, to avoid a more complex handling
        # of the session
        pack_names = [pack.name.replace('_by_' + context.bot.username, '') for pack in packs_by_title]  # strip the '_by_bot' part

    if not packs_by_title:
        logger.error('cannot find any pack with this title: %s', selected_title)
        update.message.reply_text(Strings.ADD_STICKER_SELECTED_TITLE_DOESNT_EXIST.format(selected_title[:150]))
        # do not change the user status
        return WAITING_TITLE

    if len(packs_by_title) > 1:
        logger.info('user has multiple packs with this title: %s', selected_title)

        markup = Keyboard.from_list(pack_names, add_back_button=True)

        # list with the links to the involved packs
        pack_links = ['<a href="{}">{}</a>'.format(utils.name2link(pack_name, bot_username=context.bot.username), pack_name) for pack_name in pack_names]
        text = Strings.ADD_STICKER_SELECTED_TITLE_MULTIPLE.format(selected_title, '\n• '.join(pack_links))
        update.message.reply_html(text, reply_markup=markup)

        return WAITING_NAME  # we now have to wait for the user to tap on a pack name

    logger.info('there is only one pack with the selected title, proceeding...')
    pack_name = '{}_by_{}'.format(pack_names[0], context.bot.username)

    context.user_data['pack'] = dict(name=pack_name)
    pack_link = utils.name2link(pack_name)
    update.message.reply_html(Strings.ADD_STICKER_PACK_SELECTED.format(pack_link), reply_markup=Keyboard.HIDE)

    return WAITING_STICKERS


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
def on_pack_name(update: Update, context: CallbackContext):
    logger.info('%d: user selected the pack name from the keyboard', update.effective_user.id)
    logger.debug('user_data: %s', context.user_data)

    if re.search(r'^GO BACK$', update.message.text, re.I):
        with session_scope() as session:
            pack_titles = [t.title for t in session.query(Pack.title).filter_by(user_id=update.effective_user.id).all()]

        markup = Keyboard.from_list(pack_titles)
        update.message.reply_text(Strings.ADD_STICKER_SELECT_PACK, reply_markup=markup)

        return WAITING_TITLE

    # the buttons list has the name without "_by_botusername"
    selected_name = '{}_by_{}'.format(update.message.text, context.bot.username)

    with session_scope() as session:
        pack_name = session.query(Pack).filter_by(title=selected_name).first().name

    if not pack_name:
        logger.error('user %d does not have any pack with name %s', update.effective_user.id, selected_name)
        update.message.reply_text(Strings.ADD_STICKER_SELECTED_NAME_DOESNT_EXIST)
        # do not reset the user status
        return WAITING_NAME

    context.user_data['pack'] = dict(name=pack_name)
    pack_link = utils.name2link(pack_name)
    update.message.reply_html(Strings.ADD_STICKER_PACK_SELECTED.format(pack_link), reply_markup=Keyboard.HIDE)

    return WAITING_STICKERS


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
def on_animated_sticker_receive(update: Update, _):
    logger.info('%d: user sent an animated sticker', update.effective_user.id)

    update.message.reply_text(Strings.ADD_STICKER_ANIMATED_UNSUPPORTED)

    return WAITING_STICKERS


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
def on_sticker_receive(update: Update, context: CallbackContext):
    logger.info('%d: user sent a sticker to add', update.effective_user.id)
    logger.debug('user_data: %s', context.user_data)

    name = context.user_data['pack'].get('name', None)
    if not name:
        logger.error('pack name missing (%s)', name)
        update.message.reply_text(Strings.ADD_STICKER_PACK_DATA_MISSING)

        context.user_data.pop('pack', None)  # remove temp info

        return ConversationHandler.END

    sticker = StickerFile(update.message.sticker or update.message.document, caption=update.message.caption)
    sticker.download(prepare_png=True)

    pack_link = utils.name2link(name)

    try:
        sticker.add_to_set(context.bot, update.effective_user.id, name)
    except error.PackFull:
        update.message.reply_html(Strings.ADD_STICKER_PACK_FULL.format(pack_link), quote=True)
    except error.FileDimensionInvalid:
        logger.error('resized sticker has the wrong size: %s', str(sticker))
        update.message.reply_html(Strings.ADD_STICKER_SIZE_ERROR.format(*sticker.size), quote=True)
    except error.PackInvalid:
        # pack name invalid or that pack has been deleted: delete it from the db
        with session_scope() as session:
            deleted_rows = session.query(Pack).filter(Pack.user_id==update.effective_user.id, Pack.name==name).delete('fetch')
            logger.debug('rows deleted: %d', deleted_rows or 0)

            # get the remaining packs' titles
            pack_titles = [t.title for t in session.query(Pack.title).filter_by(user_id=update.effective_user.id).all()]

        if not pack_titles:
            # user doesn't have any other pack to chose from, reset his status
            update.message.reply_html(Strings.ADD_STICKER_PACK_NOT_VALID_NO_PACKS.format(pack_link))

            logger.debug('calling sticker.delete()...')
            sticker.delete()
            return ConversationHandler.END
        else:
            # make the user select another pack from the keyboard
            markup = Keyboard.from_list(pack_titles)
            update.message.reply_html(Strings.ADD_STICKER_PACK_NOT_VALID.format(pack_link), reply_markup=markup)
            context.user_data['pack'].pop('name', None)  # remove temporary data

            logger.debug('calling sticker.delete()...')
            sticker.delete()
            return WAITING_TITLE
    except error.UnknwonError as e:
        update.message.reply_html(Strings.ADD_STICKER_GENERIC_ERROR.format(pack_link, e.message), quote=True)
    else:
        # success
        update.message.reply_html(Strings.ADD_STICKER_SUCCESS.format(pack_link), quote=True)
    finally:
        # is this entered even when we enter the "else"?
        logger.debug('calling sticker.delete()...')
        sticker.delete()
        return WAITING_STICKERS


stickersbot.add_handler(ConversationHandler(
    name='adding_stickers',
    entry_points=[CommandHandler(['add', 'a'], on_add_command)],
    states={
        WAITING_TITLE: [MessageHandler(Filters.text, on_pack_title)],
        WAITING_NAME: [MessageHandler(Filters.text, on_pack_name)],
        WAITING_STICKERS: [
            MessageHandler(
                CustomFilters.static_sticker | Filters.document.category('image/png'),
                on_sticker_receive
            ),
            MessageHandler(CustomFilters.animated_sticker, on_animated_sticker_receive),
        ]
    },
    fallbacks=[CommandHandler(['cancel', 'c', 'done', 'd'], cancel_command)]
))
