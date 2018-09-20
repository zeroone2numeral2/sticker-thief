import toml


HANDLERS = (
    'cancel',  # needs to be the first one
    'start',
    'topng',
    'packcreation',
    'addsticker',
    'removesticker',
    'forgetme',
    'list',
    'export',
    'admin'
)


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


config = toml.load('config.toml', AttrDict)
