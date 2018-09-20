START_MESSAGE = """Hello there,
I've been made to create custom sticker packs from existing stickers or PNG files.

Main commands:
/create to create a new pack
/add to add stickers to an existing pack
/help for more commands"""

HELP_MESSAGE = """<b>Full commands list</b>:
- /create: create a new pack
- /add: add a sticker to a pack
- /remove: remove a sticker from its pack
- send me a sticker file and I will send you its png back
- /list: list your packs (max 100 entries)
- /export: export a sticker pack as a zip of png files
- /forgetme: delete yourself from my database. The packs you created will <b>not</b> be deleted from Telegram

<b>Other operations</b>
You can delete a pack, change stickers' emojis/position and see stickers/packs stats from @stickers

<b>Tips</b>:
- when adding a sticker or creating a pack, you can either pass a sticker or a png file
- when adding a sticker as png, you can pass its emojis in the caption

<b>Other info</b>
All the packs you create with me have their links ending by "_by_{}". This is not made on purpose, \
but something forced by Telegram

<b>Correct way of building your own custom pack</b>
Use @MyPackBot. It doesn't steal stickers like I do. It's blazing fast too. Really suggested"""

PACK_CREATION_WAITING_TITLE = """Please send me the pack title (must not exceed 64 characters).
Use /cancel to cancel"""

PACK_TITLE_TOO_LONG = """I'm sorry, the title must be at max 64 characters long. Try with another title"""

PACK_TITLE_CONTAINS_NEWLINES = """I'm sorry, the title must be a single line (no newline characters)"""

PACK_CREATION_WAITING_NAME = """Good, this is going to be the pack title: <i>{}</i>

Please send the what will be the pack link (must be at max {} characters long)"""

PACK_NAME_TOO_LONG = """I'm sorry, this link is too long ({}/{}). Try again with another link"""

PACK_NAME_INVALID = """<b>Invalid link</b>. A link must:
• start with a letter
• consist exclusively of letters, digits or underscores
• not contain two consecutive underscores
• not end with an underscore

Please try again"""

PACK_NAME_DUPLICATE = """I'm sorry, you already have a pack with this link saved. try with another link"""

PACK_CREATION_WAITING_FIRST_STICKER = """got it, we are almost done. Now send me the first sticker of the pack"""

PACK_CREATION_FIRST_STICKER_PACK_DATA_MISSING = """Ooops, something went wrong.
Please repeat the creation process with /create"""

PACK_CREATION_ERROR_DUPLICATE_NAME = """I'm sorry, there's already a pack with <a href="{}">this link</a>.
Please send me a new link, or /cancel"""

PACK_CREATION_ERROR_INVALID_NAME = """I'm sorry, Telegram rejected the link you provided saying it's not valid.
Please send a me new link, or /cancel"""

PACK_CREATION_ERROR_GENERIC = """Error while trying to create the pack: <code>{}</code>.
Please try again, or /cancel"""

PACK_CREATION_PACK_CREATED = """Your pack has been created, add it through <a href="{}">this link</a>
Continue to send me stickers to add more, or use /cancel"""

ADD_STICKER_SELECT_PACK = """Select the pack you want to add stickers to, or /cancel"""

ADD_STICKER_NO_PACKS = """You don't have any pack yet. Use /create to start creating a new pack"""

ADD_STICKER_SELECTED_TITLE_DOESNT_EXIST = """It seems like the pack "{}" doesn't exist.
Please select a valid pack from the keyboard"""

ADD_STICKER_SELECTED_TITLE_MULTIPLE = """It seems like you have multiple packs that match the title "{}".
Please select the pack you want to choose from the keyboard below. Packs reference:
• {}"""

ADD_STICKER_PACK_SELECTED = """Good, we are going to add stickers to <a href="{}">this pack</a>.
Send me a sticker or a png file"""

ADD_STICKER_SELECTED_NAME_DOESNT_EXIST = """It seems like the pack "{}" doesn't exist.
Please select a valid pack from the keyboard"""

ADD_STICKER_PACK_DATA_MISSING = """Ooops, something went wrong.
Please repeat the process with /add"""

ADD_STICKER_PACK_NOT_VALID = """Ooops, it looks like <a href="{}">this pack</a> doesn't exist.
Please select another pack"""

ADD_STICKER_PACK_NOT_VALID_NO_PACKS = """Ooops, it looks like <a href="{}">this pack</a> doesn't exist.
Please create a new pack with /create"""

ADD_STICKER_SUCCESS = """Sticker added to <a href="{}">this pack</a>.
Continue to send me stickers to add more, use /cancel when you're done"""

ADD_STICKER_PACK_FULL = """I'm sorry, <a href="{}">this pack</a> is full (120 stickers), \
you can no longer add stickers to it. Use /remove to remove some stickers
Use /cancel when you've finished"""

ADD_STICKER_GENERIC_ERROR = """An error occurred while adding this sticker to <a href="{}">this pack</a>: \
<code>{}</code>.
Try again, send me another sticker or use /cancel when you're done"""

REMOVE_STICKER_SUCCESS = """Sticker removed from <a href="{}">its pack</a>.
Send me another sticker to remove, or /cancel when you're done"""

REMOVE_STICKER_FOREIGN_PACK = """This sticker is from a <a href="{}">pack</a> you didn't create through me. \
Try with a valid sticker, or /cancel"""

REMOVE_STICKER_ALREADY_DELETED = """This sticker is no longer part of <a href="{}">the pack</a>, \
try with another sticker"""

REMOVE_STICKER_GENERIC_ERROR = """An error occurred while removing this sticker from <a href="{}">this pack</a>: \
<code>{}</code>.
Try again, send me another sticker or use /cancel when you're done"""

FORGETME_SUCCESS = """Success, I've deleted all of your packs from my database"""

CANCEL = """Good, we're done with this (I was {})"""

LIST_NO_PACKS = """You don't have any pack. Use /create to create one"""

EXPORT_PACK_SELECT = """Please send me a stciker from the pack you want to export, or /cancel"""

EXPORT_PACK_NO_PACK = """This sticker doesn't belong to any pack. Please send me a stciker from a pack, or /cancel"""

EXPORT_PACK_START = """Exporting stickers from <i>{}</i>... it may take some minutes. Please hold on"""
