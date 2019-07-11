import logging

from .bot import StickersBot
from .database import Database
from config import config


stickersbot = StickersBot(token=config.telegram.token, use_context=True)
db = Database(config.sqlite.filename)


def main():
    stickersbot.import_handlers(r'bot/handlers/')
    stickersbot.run(clean=True)


if __name__ == '__main__':
    main()
