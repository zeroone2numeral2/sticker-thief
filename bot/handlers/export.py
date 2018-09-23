import logging
import os
from html import escape as html_escape
from shutil import make_archive
from shutil import rmtree

from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram import ChatAction
from telegram import ParseMode
from telegram.error import BadRequest
from telegram.error import TelegramError
from telegram.ext.dispatcher import run_async

from bot.overrides import Filters
from bot import strings as s
from bot import u
from bot import StickerFile

logger = logging.getLogger(__name__)


@u.action(ChatAction.TYPING)
@u.restricted
@u.failwithmessage
def on_export_command(bot, update, user_data):
    logger.info('%d: /export', update.effective_user.id)

    update.message.reply_text(s.EXPORT_PACK_SELECT)
    user_data['status'] = 'exporting_pack_waiting_sticker'


@run_async
@u.action(ChatAction.UPLOAD_DOCUMENT)
@u.failwithmessage
def on_sticker_receive(bot, update, user_data):
    logger.info('%d: user sent a stciker from the pack to export', update.effective_user.id)

    if not update.message.sticker.set_name:
        update.message.reply_text(s.EXPORT_PACK_NO_PACK)
        return

    sticker_set = bot.get_sticker_set(update.message.sticker.set_name)

    # use the message_id to make sure we will not end up with multiple dirs/files with the same name
    dir_name = '{}_{}/'.format(update.message.message_id, sticker_set.title)
    dir_path = 'tmp/{}'.format(dir_name)
    os.mkdir(dir_path)

    base_progress_message = s.EXPORT_PACK_START.format(html_escape(sticker_set.title))
    message_to_edit = update.message.reply_html(base_progress_message)

    total = len(sticker_set.stickers)
    progress = 0
    for sticker in sticker_set.stickers:
        sticker_file = StickerFile(sticker)
        try:
            # try to download and convert to png
            sticker_file.download(prepare_png=True, subdir=dir_name)
            # delete only the .webp file
            sticker_file.delete(keep_result_png=True)
        except Exception as e:
            logger.info('error while downloading and converting a sticker we need to export: %s', str(e))
            # make sure we delete the downloaded .webp file
            sticker_file.delete(keep_result_png=True)
        progress += 1

        # edit message every 12 stickers exported, or when we're done
        if progress == total or progress % 12 == 0:
            try:
                message_to_edit.edit_text('{} (progress: {}/{})'.format(base_progress_message, progress, total),
                                          parse_mode=ParseMode.HTML)
            except (TelegramError, BadRequest) as e:
                logger.error('error while editing progress message: %s', e.message)

    # for some reasons this still needs the reply-to message_id
    message_to_edit.reply_text(s.EXPORT_PACK_UPLOADING, reply_to_message_id=message_to_edit.message_id)

    logger.info('creating zip file...')
    zip_path = 'tmp/{}_{}'.format(update.message.message_id, sticker_set.name)
    make_archive(zip_path, 'zip', dir_path)
    zip_path += '.zip'

    logger.debug('sending zip file %s', zip_path)
    with open(zip_path, 'rb') as f:
        update.message.reply_document(f, caption='<a href="{}">{}</a>'.format(
            u.name2link(sticker_set.name),
            html_escape(sticker_set.title)
        ), parse_mode=ParseMode.HTML, quote=True)

    logger.info('cleaning up export files')
    try:
        os.remove(zip_path)  # remove the zip file
        rmtree(dir_path)  # remove the png dir
    except Exception as e:
        logger.error('error while cleaning up the export files: %s', str(e))

    user_data['status'] = ''  # reset the user status, do not implicitly wait for new packs to export


HANDLERS = (
    CommandHandler(['export', 'e'], on_export_command, filters=Filters.status(''), pass_user_data=True),
    MessageHandler(Filters.sticker & Filters.status('exporting_pack_waiting_sticker'), on_sticker_receive,
                   pass_user_data=True)
)
