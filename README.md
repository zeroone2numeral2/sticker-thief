# Stickers thief bot

I made this bot because I was exausted of wasting my time looking for _that_ perfect sticker to use among all my installed packs.

Features:

- create static and animated stickerpacks
- add stickers to an existing pack just by sending other stickers (png files are accepted too)
- automatically resize png files so they can fit Telegram's rateo size requirements
- remove stickers from a pack
- convert stickers to png files (and resize them if they're too big)
- export a sticker pack as a zip of png files

## Disclaimer

Using this kind of bots is an horrible solution. You are taking away from the community content made by other users to anonymize it by including it in your custom packs. This strongly arms good packs' sharing - and sometimes stickers appropriation may also fall into copyright infringement.

If you respect other people's work, want to give credits to the original pack creators and want to share the packs from which you took your favourite stickers, please use [@MyPackBot](https://t.me/MyPackBot). I can guarantee you this bot is great

## Running the bot

1. install requirements with `pip3 install -r requirements.txt`
2. rename `config.example.toml` to `config.toml` and change relevant values (that is, `telegram.token` and `telegram.admins`)
3. run the bot with `python3 main.py`

### Pyrogram integration

[Pyrogram](https://docs.pyrogram.org/) is an MTProto client, that is, a software (a Python library, in this case) that allows to interact with the [Telegram API](https://core.telegram.org/api#telegram-api) (not to be confused with the [bot API](https://core.telegram.org/api#bot-api)).

The Telegram API is mainly designed to let organic user accounts interact with Telegram, but it also allows to login as a bot (fun fact: the bot API is just an http interface that exposes some methods to simply let your bot login and interact with the Telegram API). 
By skipping the bot API middleware and connecting directly to the Telegram API, we are allowed to use a set of methods which are not exposed by the standard bot API, and that we wouldn't be able to use otherwise.

_**So, what we need Pyrogram for?**_ This bot makes use of Pyrogram to overcome a bot API limitation: 
 when a bot (or, to be fair, any user) receives a sticker, Telegram will tell the receiver only the _main_ emoji associated with that sticker object. 
 This behavior is designed into the Telegram API, so it is obviously inherited by the bot API.
 This is not ideal in our context, because when we add a sticker to a pack, we are able to tell Telegram only one emoji to bind to it (the sticker's main one).
To get a sticker's full list of emojis, we have to request to the API the _whole_ pack, which in fact is the only way to obtain this information. This request can be executed only by authenticating as a bot account through the Telegram API.

_**Does this mean the bot is not using the bot API, but directly uses the Telegram API instead?**_ No, all the interaction with Telegram are still done through the bot API. 
But, when we need to fetch a stciker's emojis, we briefly authenticate to the Telegram API (by starting a Pyrogram client) and execute an API call to fecth the sticker's pack which, as we already know, contains the emojis list.

By default, the bot doesn't make use of Pyrogram. 
You can enable it from the `pyrogram` config section, by switching `enabled` to `true`. Important: you also need to fill `api_id` and `api_hash` with your tokens, which can be obtained by following [this guide](https://docs.pyrogram.org/intro/quickstart#get-pyrogram-real-fast) from the Pyrogram documentation (pay attention to #2).

### Notes for those who are going to run this

This bot is not made to be used by a large amount of users and I cannot guarantee its performances.

By default, everyone can use this bot (with the exception of some special commands, listed below). If you want to restrict its use to only the users listed in `telegram.admins` (`condfig.toml` file), open `config.toml` and change `telegram.admins_only` to `true`.

When you pull from git, make sure to run alembic to upgrade your database schema: `alembic upgrade head`
