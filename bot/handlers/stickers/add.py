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
from bot import db
from bot import markups as rm
from bot.stickers import StickerFile
from ..fallback_commands import cancel_command
from ...utils import decorators
from ...utils import utils

logger = logging.getLogger(__name__)

WAITING_TITLE, WAITING_NAME, WAITING_STICKERS = range(3)


@decorators.action(ChatAction.TYPING)
@decorators.restricted
@decorators.failwithmessage
def on_add_command(update: Update, _):
    logger.info('%d: /add', update.effective_user.id)

    pack_titles = db.get_pack_titles(update.effective_user.id)
    if not pack_titles:
        update.message.reply_text(Strings.ADD_STICKER_NO_PACKS)

        return ConversationHandler.END
    else:
        markup = rm.get_markup_from_list(pack_titles)
        update.message.reply_text(Strings.ADD_STICKER_SELECT_PACK, reply_markup=markup)

        return WAITING_TITLE


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
def on_pack_title(update: Update, context: CallbackContext):
    logger.info('%d: user selected the pack title from the keyboard', update.effective_user.id)

    selected_title = update.message.text
    pack_info = db.get_packs_by_title(update.effective_user.id, selected_title, as_obj=True)

    if pack_info is None:
        logger.error('cannot find any pack with this title: %s', selected_title)
        update.message.reply_text(Strings.ADD_STICKER_SELECTED_TITLE_DOESNT_EXIST.format(selected_title[:150]))
        # do not change the user status
        return WAITING_TITLE

    if len(pack_info) > 1:
        logger.info('user has multiple packs with this title: %s', selected_title)

        # build the keyboard with the pack links
        pack_names = [pack.name.replace('_by_' + context.bot.username, '') for pack in pack_info]  # strip the '_by_bot' part
        markup = rm.get_markup_from_list(pack_names, add_back_button=True)

        # list with the links to the involved packs
        pack_links = ['<a href="{}">{}</a>'.format(utils.name2link(pack.name), pack.name.replace('_by_' + context.bot.username, '')) for pack in pack_info]
        text = Strings.ADD_STICKER_SELECTED_TITLE_MULTIPLE.format(selected_title, '\n• '.join(pack_links))
        update.message.reply_html(text, reply_markup=markup)

        return WAITING_NAME  # we now have to wait for the user to tap on a pack name

    logger.info('there is only one pack with the selected title, proceeding...')
    pack = pack_info[0]

    context.user_data['pack'] = dict(name=pack.name)
    pack_link = utils.name2link(pack.name)
    update.message.reply_html(Strings.ADD_STICKER_PACK_SELECTED.format(pack_link), reply_markup=rm.HIDE)

    return WAITING_STICKERS


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
def on_pack_name(update: Update, context: CallbackContext):
    logger.info('%d: user selected the pack name from the keyboard', update.effective_user.id)
    logger.debug('user_data: %s', context.user_data)

    if re.search(r'^GO BACK$', update.message.text, re.I):
        pack_titles = db.get_pack_titles(update.effective_user.id)
        markup = rm.get_markup_from_list(pack_titles)
        update.message.reply_text(Strings.ADD_STICKER_SELECT_PACK, reply_markup=markup)

        return WAITING_TITLE

    # the buttons list has the name without "_by_botusername"
    selected_name = '{}_by_{}'.format(update.message.text, context.bot.username)

    pack = db.get_pack_by_name(update.effective_user.id, selected_name, as_namedtuple=True)
    if not pack:
        logger.error('user %d does not have any pack with name %s', update.effective_user.id, selected_name)
        update.message.reply_text(Strings.ADD_STICKER_SELECTED_NAME_DOESNT_EXIST)
        # do not reset the user status
        return WAITING_NAME

    context.user_data['pack'] = dict(name=pack.name)
    pack_link = utils.name2link(pack.name)
    update.message.reply_html(Strings.ADD_STICKER_PACK_SELECTED.format(pack_link), reply_markup=rm.HIDE)

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

    error = sticker.add_to_set(context.bot, update.effective_user.id, name)
    pack_link = utils.name2link(name)
    if not error:
        update.message.reply_html(Strings.ADD_STICKER_SUCCESS.format(pack_link), quote=True)
    elif error == 14:
        update.message.reply_html(Strings.ADD_STICKER_PACK_FULL.format(pack_link), quote=True)
    elif error == 17:
        logger.error('resized sticker has the wrong size: %s', str(sticker))
        update.message.reply_html(Strings.ADD_STICKER_SIZE_ERROR.format(*sticker.size), quote=True)
    elif error == 11:
        # pack name invalid or that pack has been deleted: delete it from the db
        deleted_rows = db.delete_pack(update.effective_user.id, name)
        logger.debug('rows deleted: %d', deleted_rows or 0)

        # get the remaining packs' titles
        pack_titles = db.get_pack_titles(update.effective_user.id)
        if not pack_titles:
            # user doesn't have any other pack to chose from, reset his status
            update.message.reply_html(Strings.ADD_STICKER_PACK_NOT_VALID_NO_PACKS.format(pack_link))

            sticker.delete()
            return ConversationHandler.END
        else:
            # make the user select another pack from the keyboard
            markup = rm.get_markup_from_list(pack_titles)
            update.message.reply_html(Strings.ADD_STICKER_PACK_NOT_VALID.format(pack_link), reply_markup=markup)
            context.user_data.pop('pack', None)  # remove temporary data

            sticker.delete()
            return WAITING_TITLE
    else:
        update.message.reply_html(Strings.ADD_STICKER_GENERIC_ERROR.format(pack_link, error), quote=True)

        sticker.delete()
        return WAITING_STICKERS


stickersbot.add_handler(ConversationHandler(
    name='adding_stickers',
    entry_points=[CommandHandler(['add', 'a'], on_add_command)],
    states={
        WAITING_TITLE: [MessageHandler(Filters.text, on_pack_title)],
        WAITING_NAME: [MessageHandler(Filters.text, on_pack_name)],
        WAITING_STICKERS: [MessageHandler((Filters.sticker | Filters.png), on_sticker_receive)]
    },
    fallbacks=[CommandHandler(['cancel', 'c', 'done', 'd'], cancel_command)]
))
