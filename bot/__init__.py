from .utils import utils
from .database import base
from .bot import StickersBot
from config import config


stickersbot = StickersBot(token=config.telegram.token, use_context=True, workers=1)


def main():
    utils.load_logging_config('logging.json')

    stickersbot.import_handlers(r'bot/handlers/')
    stickersbot.run(clean=True)


if __name__ == '__main__':
    main()
