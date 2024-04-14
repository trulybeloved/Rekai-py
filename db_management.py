## built-in libraries
import os.path
import typing
import sqlite3

## third-party libraries
from loguru import logger
import aiosqlite
import cryptography
from cryptography.fernet import Fernet

## custom modules
from appconfig import AppConfig
from custom_modules.custom_exceptions import EntryNotFound


# TODO


class DBM:
    # BASE CLASS
    # Base variables

    # logging
    deep_log: bool = AppConfig.deep_log_databases

    # placeholder variables
    db_connection = sqlite3.connect('')

    _database_name = 'base_db'
    _instance = None
    _db_path: str = ''
    _main_table_name = ''
    _archive_table_name = ''
    _key_column_name = ''  # the column in which the unique string that was transmuted is stored
    _output_column_name = ''

    cached_raw_lines_dict: dict = {}
    db_updated: bool

    @property
    def db_path(self):
        return self._db_path

    def __init__(self, mode: int = 0) -> None:
        """
        SET MODE: int as 1 to prevent opening of a connection if using async functions
        """

        self._db_structure = \
            [
                [self._main_table_name, ['id', self._key_column_name, self._output_column_name, 'timestamp']],
                [self._archive_table_name, ['id', self._key_column_name, self._output_column_name, 'timestamp']]
            ]

        self._db_data_types = {
            'id': 'INTEGER PRIMARY KEY',
            self._key_column_name: 'TEXT',
            self._output_column_name: 'TEXT',
            'timestamp': 'INTEGER'
        }

        self._main_table_create_query = f'CREATE TABLE IF NOT EXISTS {self._main_table_name} (id INTEGER PRIMARY KEY, {self._key_column_name} TEXT, {self._output_column_name} TEXT, timestamp INTEGER)'
        self._archive_table_create_query = f'CREATE TABLE IF NOT EXISTS {self._archive_table_name} (id INTEGER PRIMARY KEY, {self._key_column_name} TEXT, {self._output_column_name} TEXT, timestamp INTEGER)'

        if mode == 0:
            self.db_connection = sqlite3.connect(self._db_path)
            self.cached_raw_lines_dict = self.update_cached_dict_of_raw_lines()
        elif mode == 2:
            self.db_connection = sqlite3.connect(self._db_path)

        if self.deep_log:
            logger.info(f'An instance of {self._database_name} was initialized')

    def check_and_initialize(self):
        self.ensure_db_existence()
        self.initialize_db_structure()
        self.db_connection.execute('PRAGMA journal_mode=wal')  # allows for simultaneous writes to db.

    def ensure_db_existence(self):
        if not os.path.exists(self._db_path):
            os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
            with open(self._db_path, 'w'):
                pass
            logger.warning(f'{self._database_name} was not found at the specified path: {self._db_path} | Hence a blank database was created')
        else:
            if AppConfig.deep_log_databases:
                logger.info(f'{self._database_name} was found in the provided path')

    def check_db_structure(self) -> bool:
        cursor = self.db_connection.cursor()
        try:
            for [table_name, columns] in self._db_structure:
                cursor.execute(f'PRAGMA table_info({table_name})')
                existing_columns = [column[1] for column in cursor.fetchall()]
                if set(columns) != set(existing_columns):
                    return False
            return True
        except Exception as e:
            logger.error(f'{self._database_name}:An Exception:{e} was raised')
            return False

    def initialize_db_structure(self) -> None:
        structure_test = self.check_db_structure()
        if structure_test is True:
            if self.deep_log:
                logger.info(f'{self._database_name} is already initialized and has the correct structure.')
        else:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute(self._main_table_create_query)
                cursor.execute(self._archive_table_create_query)
                if self.deep_log:
                    logger.info(
                        f'{self._database_name}:{self._main_table_name} created. {self._archive_table_name} created. DB initialized')
                self.db_connection.commit()
                self.db_updated = True
            except Exception as e:
                logger.error(f'{self._database_name}:An Exception:{e} was raised')

    def query(self, raw_line: str, column_name:typing.Union[str, None] = None) -> typing.Union[str, bytes]:

        if column_name is None:
            column_name = self._output_column_name

        cursor = self.db_connection.cursor()
        query_query = f'SELECT {column_name} FROM {self._main_table_name} WHERE {self._key_column_name} = ?'
        cursor.execute(query_query, (raw_line,))
        query_results = cursor.fetchone()
        if query_results:
            result = query_results[0]
            if self.deep_log:
                logger.info(f'{self._database_name}:{self._database_name} Query for {raw_line} successful')
            return result
        else:
            if self.deep_log:
                logger.info(f'{self._database_name}:{raw_line} was not found in the {self._database_name} database')
            raise EntryNotFound

    def insert(self, raw_line: str, transmuted_data: typing.Union[str, bytes], unix_timestamp: int,
               column_name:typing.Union[str,None] = None) -> None:
        
        cursor = self.db_connection.cursor()

        if isinstance(transmuted_data, bytes):
            transmuted_data = sqlite3.Binary(transmuted_data)

        if column_name is None:
            column_name = self._output_column_name
        # Check if raw_line already exists in the table
        # COUNT FUNCTION returns an integer with the total number of matching rows
        check_query = f'SELECT COUNT(*) FROM {self._main_table_name} WHERE {self._key_column_name} = ?'
        cursor.execute(check_query, (raw_line,))
        count = cursor.fetchone()[0]
        if count == 0:
            # raw_line doesn't exist, so perform the insertion
            insert_query = f'INSERT INTO {self._main_table_name} ({self._key_column_name}, {column_name}, timestamp) VALUES (?, ?, ?)'
            cursor.execute(insert_query, (raw_line, transmuted_data, unix_timestamp))
            self.db_connection.commit()
            self.db_updated = True
            if self.deep_log:
                logger.info(
                    f'{self._database_name}:Insert of {column_name} for line {raw_line} in {self._main_table_name} was successful')
        else:
            self.archive(raw_line=raw_line)
            self.insert(raw_line=raw_line, transmuted_data=transmuted_data, column_name=column_name,
                        unix_timestamp=unix_timestamp)
            if self.deep_log:
                logger.info(
                    f'{self._database_name}:Insert of {column_name} into {self._main_table_name} was completed with archival of previously existing line')

    def archive(self, raw_line: str) -> None:
        cursor = self.db_connection.cursor()
        check_query = f'SELECT COUNT(*) FROM {self._main_table_name} WHERE {self._key_column_name} = ?'
        cursor.execute(check_query, (raw_line,))
        count = cursor.fetchone()[0]
        if count != 0:
            archival_query = f'INSERT INTO {self._archive_table_name} ({self._key_column_name}, {self._output_column_name}) '
            f'SELECT {self._key_column_name}, {self._output_column_name} FROM {self._main_table_name} WHERE {self._key_column_name} = ?'
            cursor.execute(archival_query, (raw_line,))
            delete_query = f'DELETE FROM {self._main_table_name} WHERE {self._key_column_name} = ?'
            cursor.execute(delete_query, (raw_line,))
            self.db_connection.commit()
            if self.deep_log:
                logger.info(f'{self._database_name}:{raw_line} archived from {self._main_table_name}')
            self.db_updated = True
        else:
            if self.deep_log:
                logger.info(f'{self._database_name}:CHECK QUERY for {raw_line} in {self._database_name} failed. '
                            f'No such entry exists. Archive function is not applicable')

    def update_cached_dict_of_raw_lines(self) -> dict:
        cursor = self.db_connection.cursor()
        list_query = f'SELECT {self._key_column_name} FROM {self._main_table_name}'
        cursor.execute(list_query)
        list_of_raw_lines_in_db = [row[0] for row in cursor.fetchall()]
        dict_of_raw_lines_in_db = {key: None for key in list_of_raw_lines_in_db}
        return dict_of_raw_lines_in_db

    def clear_archive(self) -> None:
        cursor = self.db_connection.cursor()
        clear_query = f'DELETE FROM {self._archive_table_name}'
        cursor.execute(clear_query)
        self.db_connection.commit()
        if self.deep_log:
            logger.info(f'{self._database_name}:{self._archive_table_name} Cleared')

    def clear_main_table(self) -> None:
        cursor = self.db_connection.cursor()
        clear_main_query = f'DELETE FROM {self._main_table_name}'
        cursor.execute(clear_main_query)
        self.db_connection.commit()
        if self.deep_log:
            logger.critical(f'MAIN TABLE in {self._database_name} has been cleared')
        self.db_updated = True

    def reset_database(self):
        self.clear_main_table()
        self.clear_archive()
        self.initialize_db_structure()
        if self.deep_log:
            logger.critical(f'{self._database_name} has been wiped and reset')

    def close_connection(self) -> None:
        self.db_connection.close()

    def reconnect(self) -> None:
        self.db_connection = sqlite3.connect(self._db_path)

    def get_dict_of_keystrings_in_db(self) -> dict:
        if self.db_updated:
            self.update_cached_dict_of_raw_lines()
            self.db_updated = False
            return self.cached_raw_lines_dict
        else:
            return self.cached_raw_lines_dict

    ## ASYNC FUNCTIONS

    async def async_connect_to_db(self):
        db_connection = await aiosqlite.connect(self._db_path)
        return db_connection

    async def async_ensure_database_integrity(self):
        self.ensure_db_existence()

        async with aiosqlite.connect(self._db_path) as db:
            # Enable WAL mode allowing for concurrent writes
            await db.execute('PRAGMA journal_mode=wal')

            # Database Structure Test
            structure_test: bool
            try:
                for [table_name, columns] in self._db_structure:
                    cursor = await db.execute(f'PRAGMA table_info({table_name})')
                    existing_columns = [column[1] for column in await cursor.fetchall()]
                    if set(columns) != set(existing_columns):
                        structure_test = False
                    else:
                        structure_test = True
            except Exception as e:
                logger.error(f'{self._database_name}:An Exception:{e} was raised')
                structure_test = False

            # Initialize Database Stucture if structure test fails
            if structure_test is True:
                if self.deep_log:
                    logger.info(f'{self._database_name} is already initialized and has the correct structure.')
            else:
                try:
                    await db.execute(self._main_table_create_query)
                    await db.execute(self._archive_table_create_query)
                    if self.deep_log:
                        logger.info(
                            f'{self._database_name}:{self._main_table_name} created. {self._archive_table_name} created. DB initialized')
                    await db.commit()
                    self.db_updated = True
                except Exception as e:
                    logger.error(f'{self._database_name}:An Exception:{e} was raised')

    async def async_query(self, raw_line: str, column_name:typing.Union[str, None] = None) -> typing.Union[str, bytes]:

        if column_name is None:
            column_name = self._output_column_name

        db = await self.async_connect_to_db()
        cursor = await db.cursor()
        query_query = f'SELECT {column_name} FROM {self._main_table_name} WHERE {self._key_column_name} = ?'
        await cursor.execute(query_query, (raw_line,))
        query_results = await cursor.fetchone()
        await db.close()
        if query_results:
            result = query_results[0]
            if self.deep_log:
                logger.info(f'{self._database_name}:{self._database_name} Query for {raw_line} successful')
            return result
        else:
            if self.deep_log:
                logger.info(f'{self._database_name}:{raw_line} was not found in the {self._database_name} database')
            raise EntryNotFound


    async def async_insert(self, raw_line: str, transmuted_data: typing.Union[str, bytes], unix_timestamp: int,
                           column_name:typing.Union[str,None] = None) -> None:

        db = await self.async_connect_to_db()
        cursor = await db.cursor()

        if isinstance(transmuted_data, bytes):
            transmuted_data = sqlite3.Binary(transmuted_data)

        if column_name is None:
            column_name = self._output_column_name
        # Check if raw_line already exists in the table
        # COUNT FUNCTION returns an integer with the total number of matching rows
        check_query = f'SELECT COUNT(*) FROM {self._main_table_name} WHERE {self._key_column_name} = ?'
        await cursor.execute(check_query, (raw_line,))
        count = await cursor.fetchone()
        if count[0] == 0:
            # raw_line doesn't exist, so perform the insertion
            insert_query = f'INSERT INTO {self._main_table_name} ({self._key_column_name}, {column_name}, timestamp) VALUES (?, ?, ?)'
            await cursor.execute(insert_query, (raw_line, transmuted_data, unix_timestamp))
            await db.commit()
            await db.close()
            self.db_updated = True
            if self.deep_log:
                logger.info(
                    f'{self._database_name}:Insert of {column_name} for line {raw_line} in {self._main_table_name} was successful')
        else:
            await self.async_archive(raw_line=raw_line)
            await self.async_insert(raw_line=raw_line, transmuted_data=transmuted_data, column_name=column_name,
                                    unix_timestamp=unix_timestamp)
            if self.deep_log:
                logger.info(
                    f'{self._database_name}:Insert of {column_name} into {self._main_table_name} was completed with archival of previously existing line')

    async def async_archive(self, raw_line: str) -> None:
        db = await self.async_connect_to_db()
        cursor = await db.cursor()
        check_query = f'SELECT COUNT(*) FROM {self._main_table_name} WHERE {self._key_column_name} = ?'
        await cursor.execute(check_query, (raw_line,))
        count = await cursor.fetchone()
        if count[0] != 0:
            archival_query = f'INSERT INTO {self._archive_table_name} ({self._key_column_name}, {self._output_column_name}) SELECT {self._key_column_name}, {self._output_column_name} FROM {self._main_table_name} WHERE {self._key_column_name} = ?'
            await cursor.execute(archival_query, (raw_line,))
            delete_query = f'DELETE FROM {self._main_table_name} WHERE {self._key_column_name} = ?'
            await cursor.execute(delete_query, (raw_line,))
            await db.commit()
            await db.close()
            if self.deep_log:
                logger.info(f'{self._database_name}:{raw_line} archived from {self._main_table_name}')
            self.db_updated = True
        else:
            if self.deep_log:
                logger.info(f'{self._database_name}:CHECK QUERY for {raw_line} in {self._database_name} failed. '
                            f'No such entry exists. Archive function is not applicable')

    async def async_update_cached_dict_of_raw_lines(self) -> dict:
        db = await self.async_connect_to_db()
        cursor = await db.cursor()
        list_query = f'SELECT {self._key_column_name} FROM {self._main_table_name}'
        await cursor.execute(list_query)
        list_of_raw_lines_in_db = [row[0] for row in await cursor.fetchall()]
        dict_of_raw_lines_in_db = {key: None for key in list_of_raw_lines_in_db}
        await db.close()
        return dict_of_raw_lines_in_db

class JishoParseDBM(DBM):
    # intrinsic settings
    _database_name = 'jisho_parse_db'
    _instance = None
    _db_path = AppConfig.jisho_parse_db_path

    _main_table_name = 'jisho_parse'
    _archive_table_name = 'jisho_parse_archive'

    _key_column_name = 'raw_line'  # the column in which the unique string that was transmuted is stored
    _output_column_name = 'parsed_html'

    # operational flags
    db_updated = False

    # def __new__(cls, *args, **kwargs):
    #     if cls._instance is None:
    #         cls._instance = super(JishoParseDBM, cls).__new__(cls)
    #     return cls._instance


class TextToSpeechDBM(DBM):
    # intrinsic settings
    _database_name = 'je_tts'
    _instance = None
    _db_path = AppConfig.je_tts_db

    _main_table_name = 'je_tts'
    _archive_table_name = 'je_tts_archive'

    _key_column_name = 'raw_line'
    _output_column_name = 'tts_bytes'

    # operational flags
    db_updated = False

    # def __new__(cls, *args, **kwargs):
    #     if cls._instance is None:
    #         cls._instance = super(TextToSpeechDBM, cls).__new__(cls)
    #     return cls._instance


class DeepLDBM(DBM):
    # intrinsic settings
    _database_name = 'deepl_tl'
    _instance = None
    _db_path = AppConfig.deepl_tl_db_path

    _main_table_name = 'deepl_tl'
    _archive_table_name = 'deepl_tl_archive'

    _key_column_name = 'raw_line'  # the column in which the unique string that was transmuted is stored
    _output_column_name = 'deepl_tl'

    # operational flags
    db_updated = False

    # def __new__(cls, *args, **kwargs):
    #     if cls._instance is None:
    #         cls._instance = super(DeepLDBM, cls).__new__(cls)
    #     return cls._instance


class GoogleTLDBM(DBM):
    # intrinsic settings
    _database_name = 'google_tl'
    _instance = None
    _db_path = AppConfig.google_tl_db_path

    _main_table_name = 'google_tl'
    _archive_table_name = 'google_tl_archive'

    _key_column_name = 'raw_line'  # the column in which the unique string that was transmuted is stored
    _output_column_name = 'google_tl'

    # operational flags
    db_updated = False

    # def __new__(cls, *args, **kwargs):
    #     if cls._instance is None:
    #         cls._instance = super(GoogleTLDBM, cls).__new__(cls)
    #     return cls._instance


class OpenAIGPTDBM(DBM):
    # intrinsic settings
    _database_name = 'openai_gpt_infer'
    _instance = None
    _db_path = AppConfig.openai_gpt_db_path

    _main_table_name = 'gpt_infer'
    _archive_table_name = 'gpt_infer_archive'

    _key_column_name = 'db_key_string'  # the column in which the unique string that was transmuted is stored
    _output_column_name = 'inference'

    # operational flags
    db_updated = False

    # def __new__(cls, *args, **kwargs):
    #     if cls._instance is None:
    #         cls._instance = super(GoogleTLDBM, cls).__new__(cls)
    #     return cls._instance


class SystemDBM:

    _database_name = 'system_db'
    _instance = []
    _db_path = AppConfig.system_db_path

    deep_log: bool = AppConfig.deep_log_databases

    _db_structure = \
        [
            ['app_state',
                [
                'id INTEGER PRIMARY KEY',
                'first_run INTEGER',
                'deepl_api_available INTEGER',
                'google_auth_configured INTEGER'
                ]
            ],
            ['app_config', ['id INTEGER PRIMARY KEY', 'app_config_json TEXT', 'timestamp INTEGER']],
            ['run_config', ['id INTEGER PRIMARY KEY', 'run_config_json TEXT', 'timestamp INTEGER']],
            ['api_crypt', ['id INTEGER PRIMARY KEY', 'api_name TEXT', 'encrypted_api_key TEXT']],
            ['url_crypt', ['id INTEGER PRIMARY KEY', 'service_name TEXT', 'encrypted_url TEXT']]
        ]

    @property
    def db_path(self):
        return self._db_path

    def __init__(self):
        try:
            self.db_connection = sqlite3.connect(self._db_path)
        except:
            self.check_connect_initialize()

        self.secrets_dir = AppConfig.secrets_dir
        self.key_file = os.path.join(self.secrets_dir, 'system_db.key')
        self.key = None

        self.generate_key()
        self.load_key()

    def check_connect_initialize(self):
        self.ensure_db_existence()
        self.db_connection = sqlite3.connect(self._db_path)
        self.initialize_db_structure()
        self.db_connection.execute('PRAGMA journal_mode=wal')  # allows for simultaneous writes to db.

    def ensure_db_existence(self):
        if not os.path.exists(self._db_path):
            os.makedirs(os.path.dirname(self._db_path), exist_ok=True)
            with open(self._db_path, 'w'):
                pass
            logger.warning(f'{self._database_name} was not found at the specified path: {self._db_path} | Hence a blank database was created')
        else:
            if AppConfig.deep_log_databases:
                logger.info(f'{self._database_name} was found in the provided path')

    def check_db_structure(self) -> bool:
        cursor = self.db_connection.cursor()
        try:
            for [table_name, columns] in self._db_structure:
                cursor.execute(f'PRAGMA table_info({table_name})')
                existing_columns = [column[1] for column in cursor.fetchall()]
                if set(columns) != set(existing_columns):
                    return False
            return True
        except Exception as e:
            logger.error(f'{self._database_name}:An Exception:{e} was raised')
            return False

    def initialize_db_structure(self) -> None:
        structure_test = self.check_db_structure()
        if structure_test is True:
            if self.deep_log:
                logger.info(f'{self._database_name} is already initialized and has the correct structure.')
        else:
            try:
                cursor = self.db_connection.cursor()
                for table in self._db_structure:
                    table_name = table[0]
                    columns = table[1]
                    coloumns_sql_substring = ','.join(columns)
                    table_create_query = f'CREATE TABLE IF NOT EXISTS {table_name} ({coloumns_sql_substring})'
                    cursor.execute(table_create_query)

                self.db_connection.commit()
                self.db_updated = True

                if self.deep_log:
                    logger.info(
                        f'{self._database_name}: Tables created. DB initialized')

            except Exception as e:
                logger.error(f'{self._database_name}:An Exception:{e} was raised')

    def generate_key(self):
        if not os.path.exists(self.key_file):
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as kf:
                kf.write(key)

    def load_key(self):
        with open(self.key_file, 'rb') as kf:
            self.key = kf.read()

    def encrypt(self, data):
        cipher = Fernet(self.key)
        return cipher.encrypt(data.encode())

    def decrypt(self, encrypted_data):
        cipher = Fernet(self.key)
        return cipher.decrypt(encrypted_data).decode()

    def close_connection(self) -> None:
        self.db_connection.close()

    def reconnect(self) -> None:
        self.db_connection = sqlite3.connect(self._db_path)

    def execute(self, query, params=None):
        if not self.db_connection:
            self.reconnect()
        cursor = self.db_connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        self.db_connection.commit()
        return cursor

    def create_table(self, table_name, columns):
        column_defs = ", ".join(columns)
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_defs})"
        self.execute(query)

    def insert(self, table_name, data):
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        params = tuple(data.values())
        self.execute(query, params)

    def fetch_all(self, table_name):
        query = f"SELECT * FROM {table_name}"
        result = self.execute(query).fetchall()
        return result
