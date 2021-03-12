class Strings:
    START_MESSAGE = ("Hello there,\n"
                     "You can use me to create custom sticker packs using existing stickers or PNG files.\n"
                     "\n"
                     "Main commands:\n"
                     "/create to create a new pack\n"
                     "/add to add stickers to an existing pack\n"
                     "/help for more commands\n")

    HELP_MESSAGE = ("<b>Full commands list</b>:\n"
                    "- /create: create a new pack (animated packs are supported)\n"
                    "- /add: add a sticker to a pack\n"
                    "- /remove: remove a sticker from its pack\n"
                    "- send me a sticker and I will send you its png back\n"
                    "- /list: list your packs (max 100 entries)\n"
                    "- /export: export a sticker pack as a zip of png files\n"
                    "- /forgetme: delete yourself from my database. The packs you created will <b>not</b> be deleted from Telegram\n"
                    "- /cleanup: remove from the list of your packs all the packs that you have deleted using @stickers\n"
                    "\n"
                    "<b>Other operations</b>\n"
                    "You can delete a pack, change a sticker's emojis, change stickers order and see a sticker/pack stats from @stickers\n"
                    "\n"
                    "<b>Tips</b>:\n"
                    "- when adding a sticker, you can set its emojis by sending them before sending the sticker\n"
                    "- when adding a sticker or creating a pack, you can either pass a sticker or a png file\n"
                    "- when adding a sticker as png, you can pass its emojis in the caption\n"
                    "\n"
                    "<b>Other info</b>\n"
                    "All the packs you create with me have their links ending by \"_by_{}\". This is not made on purpose, "
                    "but something forced by Telegram\n"
                    "\n"
                    "<b>Correct way of building your own custom pack</b>\n"
                    "Use @MyPackBot. It doesn't steal stickers like I do. It's blazing fast too. Really suggested")

    PACK_CREATION_WAITING_TITLE = ("Alright, a new stickers pack! Select the pack type with the buttons below "
                                   "and <b>send me the pack title</b> (must not exceed 64 characters).\n\n"
                                   "Use /cancel to cancel")

    PACK_CREATION_ANIMATED_WAITING_TITLE = ("Alright, a new animated pack! Please send me the pack title "
                                            "(must not exceed 64 characters).\n"
                                            "Use /cancel to cancel")

    PACK_TITLE_TOO_LONG = "I'm sorry, the title must be at max 64 characters long. Try with another title"

    PACK_TITLE_CONTAINS_NEWLINES = "I'm sorry, the title must be a single line (no newline characters)"

    PACK_TITLE_INVALID_MESSAGE = ("Oh no! This is not what I was waiting for! Please send me the "
                                  "pack title, or /cancel")

    PACK_CREATION_WAITING_NAME = ("Good, this is going to be the pack title: <i>{}</i>\n"
                                  "\n"
                                  "Please send me what will be the pack link (must be at max {} characters long. "
                                  "<b>Doesn't</b> need to include <code>https://t.me/addstickers/</code>)")

    PACK_NAME_TOO_LONG = "I'm sorry, this link is too long ({}/{}). Try again with another link"

    PACK_NAME_INVALID = ("<b>Invalid link</b>. A link must:\n"
                         "• start with a letter\n"
                         "• consist exclusively of letters, digits or underscores\n"
                         "• not contain two consecutive underscores\n"
                         "• not end with an underscore\n"
                         "\n"
                         "Please try again")

    PACK_NAME_INVALID_MESSAGE = ("Oh no! This is not what I was waiting for! Please send me the "
                                 "pack link, or /cancel")

    PACK_NAME_DUPLICATE = "I'm sorry, you already have a pack with this link saved. try with another link"

    PACK_TYPE_BUTTONS_EXPIRED = "These buttons are no longer valid"

    PACK_TYPE_CHANGED = "Pack type: {}. Now send me the pack title!"

    PACK_CREATION_WAITING_FIRST_STATIC_STICKER = ("Got it, we are almost done. Now send me the first sticker "
                                                  "of the pack (or a png file, or the emojis to use for the sticker)")

    PACK_CREATION_WAITING_FIRST_ANIMATED_STICKER = ("Got it, we are almost done. Now send me the first animated "
                                                    "sticker of the pack (or the emojis to use for the sticker)")

    PACK_CREATION_FIRST_STICKER_PACK_DATA_MISSING = ("Ooops, something went wrong.\n"
                                                     "Please repeat the creation process with /create")

    PACK_CREATION_WAITING_FIRST_STICKER_INVALID_MESSAGE = ("Uhmm 🤔 I was waiting for the first sticker of the pack. "
                                                           "Please send me a sticker, or /cancel")

    PACK_CREATION_ERROR_DUPLICATE_NAME = ("I'm sorry, there's already a pack with <a href=\"{}\">this link</a>.\n"
                                          "Please send me a new link, or /cancel")

    PACK_CREATION_ERROR_INVALID_NAME = ("I'm sorry, Telegram rejected the link you provided saying it's not valid.\n"
                                        "Please send a me new link, or /cancel")

    PACK_CREATION_ERROR_GENERIC = ("Error while trying to create the pack: <code>{}</code>.\n"
                                   "Please try again, or /cancel")

    PACK_CREATION_PACK_CREATED = ("Your pack has been created, add it through <a href=\"{}\">this link</a>\n"
                                  "Continue to send me stickers to add more, or /done")

    ADD_STICKER_SELECT_PACK = "Select the pack you want to add stickers to, or /cancel"

    ADD_STICKER_NO_PACKS = "You don't have any pack yet. Use /create to start creating a new pack"

    ADD_STICKER_SELECTED_TITLE_DOESNT_EXIST = ("It seems like the pack \"{}\" doesn't exist.\n"
                                               "Please select a valid pack from the keyboard")

    ADD_STICKER_SELECTED_TITLE_MULTIPLE = ("It seems like you have multiple packs that match the title \"{}\".\n"
                                           "Please select the pack you want to choose from the keyboard below. Packs reference:\n"
                                           "• {}")

    ADD_STICKER_PACK_SELECTED_STATIC = ("Good, we are going to add stickers to <a href=\"{}\">this pack</a>.\n"
                                        "Send me a sticker or a png file, or /cancel")

    ADD_STICKER_PACK_SELECTED_ANIMATED = ("Good, we are going to add stickers to <a href=\"{}\">this pack</a>.\n"
                                          "Send me an animated sticker")

    ADD_STICKER_SELECTED_NAME_DOESNT_EXIST = ("It seems like the pack \"{}\" doesn't exist.\n"
                                              "Please select a valid pack from the keyboard")

    ADD_STICKER_PACK_DATA_MISSING = ("Ooops, something went wrong.\n"
                                     "Please repeat the process with /add")

    ADD_STICKER_PACK_NOT_VALID = ("Ooops, it looks like <a href=\"{}\">this pack</a> doesn't exist.\n"
                                  "Please select another pack")

    ADD_STICKER_PACK_NOT_VALID_NO_PACKS = ("Ooops, it looks like <a href=\"{}\">this pack</a> doesn't exist.\n"
                                           "Please create a new pack with /create")

    ADD_STICKER_NO_EMOJI_IN_TEXT = ("Uhm, I don't understand. Send me a sticker, or send me a list of emojis to "
                                    "use for the next sticker (or /done to exit)")

    ADD_STICKER_TOO_MANY_EMOJIS = "Whoa, that's a lot of emojis! I can only use 10 at max, please try again"

    ADD_STICKER_EMOJIS_SAVED = "Oh, some emojis! We will use these {} emojis for the next sticker you will send me: {}"

    ADD_STICKER_SUCCESS = ("Sticker added to <a href=\"{}\">this pack</a>. "
                           "Continue to send me stickers to add more, use /done when you're done")

    ADD_STICKER_SUCCESS_USER_EMOJIS = ("Sticker added to <a href=\"{}\">this pack</a> using these emojis: {}\n"
                                       "Continue to send me stickers to add more, use /done when you're done")

    ADD_STICKER_PACK_FULL = ("I'm sorry, <a href=\"{}\">this pack</a> is full ({} stickers), "
                             "you can no longer add stickers to it. Use /remove to remove some stickers\n"
                             "You've exited the \"adding stickers\" mode")

    ADD_STICKER_SIZE_ERROR = ("Whoops, it looks like an error happened while resizing the sticker "
                              "and now its dimensions are {}x{} px. I can't add this sticker to the pack due to wrong resizing logic.\n"
                              "Send me another sticker, or use /done when you're done")

    ADD_STICKER_INVALID_ANIMATED = ("It looks like this sticker is no loger compliant with the most recent "
                                    "<a href=\"https://core.telegram.org/animated_stickers\">Telegram guidelines</a> "
                                    "about animated stickers. I'm sorry but I can't add it :(\n"
                                    "You can try to send the sticker again or "
                                    "send another animated sticker (or /cancel)")

    ADD_STICKER_FLOOD_EXCEPTION = ("Uh-oh, it looks like I'm quite busy right now, I cannot create the pack. "
                                   "Please try again in {} seconds")

    ADD_STICKER_GENERIC_ERROR = ("An error occurred while adding this sticker to <a href=\"{}\">this pack</a>: "
                                 "<code>{}</code>.\n"
                                 "Try again, send me another sticker or use /done when you're done")

    ADD_STICKER_ANIMATED_UNSUPPORTED = ("I am sorry, I do not support animated stickers yet :(\n"
                                        "Please send a static sticker")

    ADD_STICKER_EXPECTING_STATIC = ("Uh-oh. I was waiting for a normal sticker, not an animated one. "
                                    "Please send me a static sticker, or /cancel")

    ADD_STICKER_EXPECTING_ANIMATED = ("Uh-oh. I was waiting for an animated sticker, not a normal one. "
                                     "Please send me an animated sticker, or /cancel")

    ADD_STICKER_INVALID_MESSAGE = "Uhmm 🤔 I was waiting for the sticker to add. Send me a sticker, or /cancel"

    REMOVE_STICKER_SELECT_STICKER = "Send me the sticker you want to remove from its pack, or /cancel"

    REMOVE_INVALID_MESSAGE = "Please send the sticker you want to remove from its pack, or /cancel"

    REMOVE_STICKER_SUCCESS = ("Sticker removed from <a href=\"{}\">its pack</a>.\n"
                              "Send me another sticker to remove, or /done when you're done")

    REMOVE_STICKER_FOREIGN_PACK = ("This sticker is from a <a href=\"{}\">pack</a> you didn't create through me. "
                                   "Try with a valid sticker, or /done")

    REMOVE_STICKER_ALREADY_DELETED = ("This sticker is no longer part of <a href=\"{}\">the pack</a>, "
                                      "try with another sticker")

    REMOVE_STICKER_GENERIC_ERROR = (
        "An error occurred while removing this sticker from <a href=\"{}\">this pack</a>: "
        "<code>{}</code>.\n"
        "Try again, send me another sticker or use /done when you're done")

    FORGETME_SUCCESS = "Success, I've deleted all of your packs from my database"

    CANCEL = "Good, we're done with that"

    CANCEL_NO_CONVERSATION = "There is no operation going on 😴"

    TIMEOUT = "😴 It looks like you are inactive, I've canceled the current operation"

    LIST_NO_PACKS = "You don't have any pack. Use /create to create one"

    LIST_FOOTER = "\n\n<b>s</b>: static\n<b>a</b>: animated"

    ANIMATED_STICKERS_NO_FILE = "Unfortunately I can't send you animated stickers back as file :("

    EXPORT_PACK_SELECT = "Please send me a stciker from the pack you want to export, or /cancel"

    EXPORT_PACK_NO_PACK = "This sticker doesn't belong to any pack. Please send me a stciker from a pack, or /cancel"

    EXPORT_PACK_START = "Exporting stickers from <i>{}</i>... it may take some minutes. Please hold on"

    EXPORT_PACK_UPLOADING = "Zipping png files and uploading..."

    EXPORT_ANIMATED_STICKERS_NOT_SUPPORTED = "Exporting animated packs is not supported yet"

    EXPORT_SKIPPED_STICKERS = " - I wasn't able to export {} stickers!"

    EXPORT_ONGOING = "Hold on, the export is processing..."

    CLEANUP_NO_PACK = ("It looks like all your packs are still there. No pack has been removed from the database.\n"
                       "If you just deleted a pack from @stickers, remember that it might take some time for bots "
                       "to be made aware of its deletion.\n\n"
                       "You can use /list to see the list of your packs")

    CLEANUP_HEADER = "These are the packs that no longer exist and has been removed from the database:\n"

    CLEANUP_WAIT = "Hold on, this operation might take some time..."

    TO_FILE_MIME_TYPE = "mime-type: {}"
