import logging
import os
from html import escape as html_escape
from shutil import make_archive
from shutil import rmtree

# noinspection PyPackageRequirements
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    Filters,
    run_async
)
# noinspection PyPackageRequirements
from telegram import ChatAction, ParseMode, Update
# noinspection PyPackageRequirements
from telegram.error import BadRequest, TelegramError

from bot import stickersbot
from bot.strings import Strings
from .fallback_commands import cancel_command
from ..utils import decorators
from ..utils import utils

from bot.stickers import StickerFile

logger = logging.getLogger(__name__)


WAITING_STICKER = range(1)


@decorators.action(ChatAction.TYPING)
@decorators.restricted
@decorators.failwithmessage
def on_export_command(update: Update, _):
    logger.info('%d: /export', update.effective_user.id)

    update.message.reply_text(Strings.EXPORT_PACK_SELECT)

    return WAITING_STICKER


@run_async
@decorators.action(ChatAction.UPLOAD_DOCUMENT)
@decorators.failwithmessage
def on_sticker_receive(update: Update, context: CallbackContext):
    logger.info('%d: user sent a stciker from the pack to export', update.effective_user.id)

    if not update.message.sticker.set_name:
        update.message.reply_text(Strings.EXPORT_PACK_NO_PACK)
        return WAITING_STICKER

    sticker_set = context.bot.get_sticker_set(update.message.sticker.set_name)

    # use the message_id to make sure we will not end up with multiple dirs/files with the same name
    dir_name = '{}_{}/'.format(update.message.message_id, sticker_set.title)
    dir_path = 'tmp/{}'.format(dir_name)
    os.mkdir(dir_path)

    base_progress_message = Strings.EXPORT_PACK_START.format(html_escape(sticker_set.title))
    message_to_edit = update.message.reply_html(base_progress_message, quote=True)

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

        # edit message every 12 exported stickers, or when we're done
        if progress == total or progress % 10 == 0:
            try:
                message_to_edit.edit_text('{} (progress: {}/{})'.format(base_progress_message, progress, total),
                                          parse_mode=ParseMode.HTML)
            except (TelegramError, BadRequest) as e:
                logger.error('error while editing progress message: %s', e.message)

    message_to_edit.reply_text(Strings.EXPORT_PACK_UPLOADING, quote=True)

    logger.info('creating zip file...')
    zip_path = 'tmp/{}_{}'.format(update.message.message_id, sticker_set.name)
    make_archive(zip_path, 'zip', dir_path)
    zip_path += '.zip'

    logger.debug('sending zip file %s', zip_path)
    with open(zip_path, 'rb') as f:
        update.message.reply_document(f, caption='<a href="{}">{}</a>'.format(
            utils.name2link(sticker_set.name),
            html_escape(sticker_set.title)
        ), parse_mode=ParseMode.HTML, quote=True)

    logger.info('cleaning up export files')
    try:
        os.remove(zip_path)  # remove the zip file
        rmtree(dir_path)  # remove the png dir
    except Exception as e:
        logger.error('error while cleaning up the export files: %s', str(e))

    return ConversationHandler.END


stickersbot.add_handler(ConversationHandler(
    name='export_command',
    entry_points=[CommandHandler(['export', 'e', 'dump'], on_export_command)],
    states={
        WAITING_STICKER: [MessageHandler(Filters.sticker, on_sticker_receive)],
    },
    fallbacks=[CommandHandler(['cancel', 'c', 'done', 'd'], cancel_command)]
))
