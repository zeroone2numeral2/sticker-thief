from telegram.ext import Updater

import bot.utils as u
from config import config
from .database import Database
from .stickers import StickerFile

updater = Updater(token=config.telegram.token)
dispatcher = updater.dispatcher

db = Database(config.sqlite.filename)
