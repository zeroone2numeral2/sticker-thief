from .utils import utils
from .overrides import *
from .bot import StickersBot
from .database import Database
from config import config


stickersbot = StickersBot(token=config.telegram.token, use_context=True)
db = Database(config.sqlite.filename)


def main():
    utils.load_logging_config('logging.json')

    stickersbot.import_handlers(r'bot/handlers/')
    stickersbot.run(clean=True)


if __name__ == '__main__':
    main()
