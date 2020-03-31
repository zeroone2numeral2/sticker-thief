import logging
from html import escape as html_escape
import zipfile
import tempfile
import json

# noinspection PyPackageRequirements
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackContext,
    run_async
)
# noinspection PyPackageRequirements
from telegram import ChatAction, ParseMode, Update
# noinspection PyPackageRequirements
from telegram.error import BadRequest, TelegramError

from bot import stickersbot
from bot.strings import Strings
from ..conversation_statuses import Status
from ..fallback_commands import cancel_command
from ...customfilters import CustomFilters
from ...utils import decorators
from ...utils import utils

from bot.sticker import StickerFile

logger = logging.getLogger(__name__)


@decorators.action(ChatAction.TYPING)
@decorators.restricted
@decorators.failwithmessage
@decorators.logconversation
def on_export_command(update: Update, _):
    logger.info('/export')

    update.message.reply_text(Strings.EXPORT_PACK_SELECT)

    return Status.WAITING_STICKER


@run_async
@decorators.action(ChatAction.UPLOAD_DOCUMENT)
@decorators.failwithmessage
@decorators.logconversation
def on_sticker_receive(update: Update, context: CallbackContext):
    logger.info('user sent a stciker from the pack to export')

    if not update.message.sticker.set_name:
        update.message.reply_text(Strings.EXPORT_PACK_NO_PACK)
        return Status.WAITING_STICKER

    sticker_set = context.bot.get_sticker_set(update.message.sticker.set_name)

    base_progress_message = Strings.EXPORT_PACK_START.format(html_escape(sticker_set.title))
    message_to_edit = update.message.reply_html(base_progress_message, quote=True)

    pack_emojis = dict()

    with tempfile.TemporaryDirectory() as tmp_dir:
        logger.info('using %s as TemporaryDirectory', tmp_dir)
        with tempfile.TemporaryFile() as tmp_file:  # temporary zip file
            with zipfile.ZipFile(tmp_file, 'w') as zip_file:

                total = len(sticker_set.stickers)
                for i, sticker in enumerate(sticker_set.stickers):
                    sticker_file = StickerFile(sticker, temp_file=tempfile.NamedTemporaryFile(dir=tmp_dir))
                    try:
                        sticker_file.download(prepare_png=True)
                        pack_emojis[sticker.file_id] = sticker.emoji
                    except Exception as e:
                        logger.info('error while downloading and converting a sticker we need to export: %s', str(e))
                    finally:
                        sticker_file.close(keep_result_png_open=True)

                    # https://stackoverflow.com/a/54202259
                    zip_file.writestr('{}.png'.format(sticker.file_id), sticker_file.png_file.read())

                    # edit message every 10 exported stickers, or when we're done
                    progress = i + 1
                    if progress == total or progress % 10 == 0:
                        try:
                            message_to_edit.edit_text('{} (progress: {}/{})'.format(base_progress_message, progress, total),
                                                      parse_mode=ParseMode.HTML)
                        except (TelegramError, BadRequest) as e:
                            logger.warning('error while editing progress message: %s', e.message)

                with tempfile.SpooledTemporaryFile() as tmp_json:
                    tmp_json.write(json.dumps(pack_emojis, indent=2).encode())
                    tmp_json.seek(0)
                    zip_file.writestr('emojis.json', tmp_json.read())

                message_to_edit.reply_text(Strings.EXPORT_PACK_UPLOADING, quote=True)

            tmp_file.seek(0)

            update.message.reply_document(
                tmp_file,
                filename='{}.zip'.format(sticker_set.name),
                caption='<a href="{}">{}</a>'.format(
                    utils.name2link(sticker_set.name),
                    html_escape(sticker_set.title)
                ),
                parse_mode=ParseMode.HTML,
                quote=True
            )

    return ConversationHandler.END


@decorators.action(ChatAction.TYPING)
@decorators.failwithmessage
@decorators.logconversation
def on_animated_sticker_receive(update: Update, _):
    logger.info('user sent an animated sticker')

    update.message.reply_text(Strings.EXPORT_ANIMATED_STICKERS_NOT_SUPPORTED)

    return Status.WAITING_STICKER


stickersbot.add_handler(ConversationHandler(
    name='export_command',
    entry_points=[CommandHandler(['export', 'e', 'dump'], on_export_command)],
    states={
        Status.WAITING_STICKER: [
            MessageHandler(CustomFilters.static_sticker, on_sticker_receive),
            MessageHandler(CustomFilters.animated_sticker, on_animated_sticker_receive),
        ],
    },
    fallbacks=[CommandHandler(['cancel', 'c', 'done', 'd'], cancel_command)]
))
