import logging
import re

from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram import ChatAction

from bot.overrides import Filters
from bot import markups as rm
from bot import strings as s
from bot import u
from bot import db
from bot import StickerFile

logger = logging.getLogger(__name__)


@u.action(ChatAction.TYPING)
@u.restricted
@u.failwithmessage
def on_add_command(bot, update, user_data):
    logger.info('%d: /add', update.effective_user.id)

    pack_titles = db.get_pack_titles(update.effective_user.id)
    if not pack_titles:
        update.message.reply_text(s.ADD_STICKER_NO_PACKS)
    else:
        markup = rm.get_markup_from_list(pack_titles)
        update.message.reply_text(s.ADD_STICKER_SELECT_PACK, reply_markup=markup)

        user_data['status'] = 'adding_waiting_pack_title'


@u.action(ChatAction.TYPING)
@u.failwithmessage
def on_pack_title(bot, update, user_data):
    logger.info('%d: user selected the pack title from the keyboard', update.effective_user.id)

    selected_title = update.message.text
    pack_info = db.get_packs_by_title(update.effective_user.id, selected_title, as_obj=True)

    if pack_info is None:
        logger.error('cannot find any pack with this title: %s', selected_title)
        update.message.reply_text(s.ADD_STICKER_SELECTED_TITLE_DOESNT_EXIST.format(selected_title[:150]))
        # do not change the user status
        return

    if len(pack_info) > 1:
        logger.info('user has multiple packs with this title: %s', selected_title)

        # build the keyboard with the pack links
        pack_names = [pack.name.replace('_by_' + bot.username, '') for pack in pack_info]  # strip the '_by_bot' part
        markup = rm.get_markup_from_list(pack_names, add_back_button=True)

        # list with the links to the involved packs
        pack_links = ['<a href="{}">{}</a>'.format(u.name2link(pack.name), pack.name.replace('_by_' + bot.username, '')) for pack in pack_info]
        text = s.ADD_STICKER_SELECTED_TITLE_MULTIPLE.format(selected_title, '\n• '.join(pack_links))
        update.message.reply_html(text, reply_markup=markup)

        user_data['status'] = 'adding_waiting_pack_name'  # we now have to wait for the user to tap on a pack name

        return

    logger.info('there is only one pack with the selected title, proceeding...')
    pack = pack_info[0]

    user_data['pack'] = dict(name=pack.name)
    pack_link = u.name2link(pack.name)
    update.message.reply_html(s.ADD_STICKER_PACK_SELECTED.format(pack_link), reply_markup=rm.HIDE)

    user_data['status'] = 'adding_stickers'


@u.action(ChatAction.TYPING)
@u.failwithmessage
def on_pack_name(bot, update, user_data):
    logger.info('%d: user selected the pack name from the keyboard', update.effective_user.id)

    if re.search(r'^GO BACK$', update.message.text, re.I):
        pack_titles = db.get_pack_titles(update.effective_user.id)
        markup = rm.get_markup_from_list(pack_titles)
        update.message.reply_text(s.ADD_STICKER_SELECT_PACK, reply_markup=markup)

        user_data['status'] = 'adding_waiting_pack_title'
        return

    selected_name = '{}_by_{}'.format(update.message.text, bot.username)  # the buttons list has the name without "_by_botusername"

    pack = db.get_pack_by_name(update.effective_user.id, selected_name, as_namedtuple=True)
    if not pack:
        logger.error('user %d does not have any pack with name %s', update.effective_user.id, selected_name)
        update.message.reply_text(s.ADD_STICKER_SELECTED_NAME_DOESNT_EXIST)
        # do not reset the user status
        return

    user_data['pack'] = dict(name=pack.name)
    pack_link = u.name2link(pack.name)
    update.message.reply_html(s.ADD_STICKER_PACK_SELECTED.format(pack_link), reply_markup=rm.HIDE)

    user_data['status'] = 'adding_stickers'


@u.action(ChatAction.TYPING)
@u.failwithmessage
def on_sticker_receive(bot, update, user_data):
    logger.info('%d: user sent a sticker to add', update.effective_user.id)

    name = user_data['pack'].get('name', None)
    if not name:
        logger.error('pack name missing (%s)', name)
        update.message.reply_text(s.ADD_STICKER_PACK_DATA_MISSING)

        user_data.pop('pack', None)  # remove temp info
        user_data['status'] = ''  # reset user status

        return

    sticker = StickerFile(update.message.sticker or update.message.document, caption=update.message.caption)
    sticker.download(prepare_png=True)

    error = sticker.add_to_set(bot, update.effective_user.id, name)
    pack_link = u.name2link(name)
    if not error:
        update.message.reply_html(s.ADD_STICKER_SUCCESS.format(pack_link), quote=True)
    elif error == 14:
        update.message.reply_html(s.ADD_STICKER_PACK_FULL.format(pack_link), quote=True)
    elif error == 11:
        # pack name invalid or that pack has been deleted: delete it from the db
        deleted_rows = db.delete_pack(update.effective_user.id, name)
        logger.debug('rows deleted: %d', deleted_rows or 0)

        # get the remaining packs' titles
        pack_titles = db.get_pack_titles(update.effective_user.id)
        if not pack_titles:
            # user doesn't have any other pack to chose from, reset his status
            update.message.reply_html(s.ADD_STICKER_PACK_NOT_VALID_NO_PACKS.format(pack_link))
            user_data['status'] = ''
        else:
            # make the user select another pack from the keyboard
            markup = rm.get_markup_from_list(pack_titles)
            update.message.reply_html(s.ADD_STICKER_PACK_NOT_VALID.format(pack_link), reply_markup=markup)
            user_data.pop('pack', None)  # remove temporary data
            user_data['status'] = 'adding_waiting_pack_title'
    else:
        update.message.reply_html(s.ADD_STICKER_GENERIC_ERROR.format(pack_link, error), quote=True)

    sticker.delete()


HANDLERS = (
    CommandHandler(['add', 'a'], on_add_command, filters=Filters.status(''), pass_user_data=True),
    MessageHandler(Filters.text & Filters.status('adding_waiting_pack_title'), on_pack_title, pass_user_data=True),
    MessageHandler(Filters.text & Filters.status('adding_waiting_pack_name'), on_pack_name, pass_user_data=True),
    MessageHandler((Filters.sticker | Filters.png) & Filters.status('adding_stickers'), on_sticker_receive,
                   pass_user_data=True)
)
