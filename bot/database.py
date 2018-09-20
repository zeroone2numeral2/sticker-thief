import logging

import simplesqlitewrap as ssw

from bot import sql

logger = logging.getLogger(__name__)


class Database(ssw.Database):
    def __init__(self, filename):
        logger.debug('initing Database module')

        ssw.Database.__init__(self, filename)

        self._init_db()

    def _init_db(self):
        logger.debug('creating tables')

        self._execute(sql.CREATE_TABLE_USERS)
        self._execute(sql.CREATE_TABLE_PACKS)

    def insert_user(self, user_id):
        logger.debug('inserting user %d', user_id)

        rows_inserted = self._execute(sql.INSERT_USER, (user_id,), rowcount=True)
        logger.debug('inserted rows: %d', rows_inserted)

        return rows_inserted

    def check_for_name_duplicates(self, user_id, pack_name):
        logger.debug('checking for duplicate names: %d, %s', user_id, pack_name)

        return bool(self._execute(sql.CHECK_PACK_NAME_PRESENCE, (user_id, pack_name), fetchfirst=True))

    def save_pack(self, user_id, pack_name, pack_title):
        logger.debug('saving pack: %d, %s, %s', user_id, pack_name, pack_title)

        return self._execute(sql.INSERT_PACK, (user_id, pack_name, pack_title), rowcount=True)

    def get_pack_titles(self, user_id):
        logger.debug('getting packs list (titles) for %d', user_id)

        packs = self._execute(sql.SELECT_PACKS_TITLE, (user_id,), fetchall=True, as_namedtuple=True)

        if not packs:
            return None
        else:
            return [pack.title for pack in packs]

    def get_packs_by_title(self, user_id, pack_title, **kwargs):
        logger.debug('getting all the packs from %d matching this title: %s', user_id, pack_title)

        return self._execute(sql.SELECT_PACKS_BY_TITLE, (user_id, pack_title), fetchall=True, **kwargs)

    def get_pack_by_name(self, user_id, pack_name, **kwargs):
        logger.debug('getting pack by name: %d %s', user_id, pack_name)

        return self._execute(sql.SELECT_PACKS_BY_NAME, (user_id, pack_name), fetchone=True, **kwargs)

    def delete_user_packs(self, user_id):
        logger.debug('deleting user packs: %d', user_id)

        return self._execute(sql.DELETE_USER_PACKS, (user_id,), rowcount=True)

    def delete_pack(self, user_id, pack_name):
        logger.debug('deleting pack %s for user %d', pack_name, user_id)

        return self._execute(sql.DELETE_USER_PACK, (user_id, pack_name), rowcount=True)

    def get_user_packs(self, user_id, **kwargs):
        logger.debug('getting packs for user %d', user_id)

        return self._execute(sql.SELECT_USER_PACKS, (user_id,), fetchall=True, **kwargs)
