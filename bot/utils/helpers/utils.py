import logging
import logging.config
import json
import re

import emoji

logger = logging.getLogger(__name__)

API_EXCEPTIONS = {
    10: 'sticker set name is already occupied',
    11: 'STICKERSET_INVALID',  # eg. trying to remove a sticker from a set the bot doesn't own
    12: 'STICKERSET_NOT_MODIFIED',
    13: 'sticker set name invalid',  # eg. starting with a number
    14: 'STICKERS_TOO_MUCH',  # pack is full
    15: 'file is too big',  # png size > 350 kb
    # 16: 'Stickerset_invalid'  # pack name doesn't exist, or pack has been deleted
    17: 'Sticker_png_dimensions'  # invalid png size
}


def load_logging_config(file_name='logging.json'):
    with open(file_name, 'r') as f:
        logging_config = json.load(f)

    logging.config.dictConfig(logging_config)


def name2link(name, bot_username=None):
    if bot_username and not name.endswith('_by_' + bot_username):
        name += '_by_' + bot_username

    return 'https://t.me/addstickers/{}'.format(name)


def get_emojis(text):
    return ''.join(c for c in text if c in emoji.UNICODE_EMOJI)
