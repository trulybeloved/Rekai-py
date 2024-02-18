## built-in libraries
import typing

## third-party libraries
from loguru import logger

import sqlite3

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

    def __init__(self) -> None:

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

        self.db_connection = sqlite3.connect(self._db_path)
        self.db_connection.execute('PRAGMA journal_mode=wal')  # allows for simultaneous writes to db.
        self.initialize_db_structure()
        self.cached_raw_lines_dict = self.update_cached_dict_of_raw_lines()
        if self.deep_log:
            logger.info(f'An instance of {self._database_name} was initialized')

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

    _db_structure = \
        [
            ['app_state',
                [
                'id',
                'first_run',
                'deepl_api_available',
                'google_auth_configured'
                ]
            ],
            ['app_config', ['id', 'app_config_dict', 'timestamp']],
            ['run_config', ['id', 'run_config_dict', 'timestamp']],
            ['api_crypt', ['id', 'api_name', 'encrypted_api_key']],
        ]

    @property
    def db_path(self):
        return self._db_path

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SystemDBM, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.db_connection = sqlite3.connect(self._db_path)


