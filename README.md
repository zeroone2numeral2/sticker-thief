# Stickers thief bot

I made this bot because I was exausted of wasting my time looking for _that_ perfect sticker to use among all my installed packs.

Features:

- create static and animated stickerpacks
- add stickers to an existing pack just by sending other stickers (png files are accepted too)
- automatically resize png files so they can fit Telegram's rateo size requirements
- remove stickers from a pack
- convert stickers to png files (and resize them if they're too big)
- export a sticker pack as a zip of png files

### Disclaimer

Using this kind of bots is an horrible solution. You are taking away from the community content made by other users to anonymize it by including it in your custom packs. This strongly arms good packs' sharing - and sometimes stickers appropriation may also fall into copyright infringement.

If you respect other people's work, want to give credits to the original pack creators and want to share the packs from which you took your favourite stickers, please use [@MyPackBot](https://t.me/MyPackBot). I can guarantee you this bot is great

### Running the bot

1. install requirements with `pip3 install -r requirements.txt`
2. rename `config.example.toml` to `config.toml` and change relevant values (that is, `telegram.token` and `telegram.admins`)
3. run the bot with `python3 main.py`

### Notes for those who are going to run this

This bot is not made to be used by a large amount of users and I cannot guarantee its performances.

By default, everyone can use this bot (with the exception of some special commands, listed below). If you want to restrict its use to only the users listed in `telegram.admins` (`condfig.toml` file), open `config.toml` and change `telegram.admins_only` to `true`.
 
