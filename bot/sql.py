CREATE_TABLE_PACKS = """CREATE TABLE IF NOT EXISTS Packs (
    pack_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER, -- owner of the pack
    title NVARCHAR(128), --title of the pack
    name NVARCHAR(64) --will also represents the link (saved with "_by_botusername")
);"""

CHECK_PACK_NAME_PRESENCE = """SELECT name
FROM Packs
WHERE user_id = ? AND name = ?;"""

INSERT_PACK = """INSERT OR IGNORE INTO Packs (user_id, name, title)
VALUES (?, ?, ?);"""

SELECT_PACKS_TITLE = """SELECT title
FROM Packs
WHERE user_id = ?;"""

SELECT_PACKS_BY_TITLE = """SELECT *
FROM Packs
WHERE user_id = ? AND title = ?;"""

SELECT_PACKS_BY_NAME = """SELECT *
FROM Packs
WHERE user_id = ? AND name = ?;"""

DELETE_USER_PACKS = """DELETE
FROM Packs
WHERE user_id = ?;"""

DELETE_USER_PACK = """DELETE
FROM Packs
WHERE user_id = ? AND name = ?;"""

SELECT_USER_PACKS = """SELECT *
FROM Packs
WHERE user_id = ?;"""
