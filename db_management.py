import sqlite3
from appconfig import AppConfig
from custom_modules.custom_exceptions import CustomExceptions
from loguru import logger
from typing import Union


# TODO
# Implement deeplTL DBM

class DBM:
    # BASE CLASS
    # Base variables

    # logging
    logger.add(sink=AppConfig.db_log_path)

    # placeholder variables
    db_connection = sqlite3.connect('')

    _database_name = 'base_db'
    _instance = None
    _db_path: str = ''
    _main_table_name = ''
    _archive_table_name = ''
    _key_column_name = ''  # the column in which the unique string that was transmuted is stored
    _output_column_name = ''
    _db_structure = \
        [
            [_main_table_name, ['id', _key_column_name, _output_column_name]],
            [_archive_table_name, ['id', _key_column_name, _output_column_name]]
        ]
    _db_data_types = {}
    _main_table_create_query = ''
    _archive_table_create_query = ''

    cached_raw_lines_dict = {}
    db_updated: bool

    @property
    def db_path(self):
        return self._db_path

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
            if AppConfig.deep_log_databases:
                logger.error(f'{self._database_name}:An Exception:{e} was raised')
            return False

    def initialize_db_structure(self) -> None:
        structure_test = self.check_db_structure()
        if structure_test is True:
            logger.info(f'{self._database_name} is already initialized and has the correct structure.')
        else:
            try:
                cursor = self.db_connection.cursor()
                cursor.execute(self._main_table_create_query)
                cursor.execute(self._archive_table_create_query)
                if AppConfig.deep_log_databases:
                    logger.info(
                        f'{self._database_name}:{self._main_table_name} created. {self._archive_table_name} created. DB initialized')
                self.db_connection.commit()
                self.db_updated = True
            except Exception as e:
                if AppConfig.deep_log_databases:
                    logger.error(f'{self._database_name}:An Exception:{e} was raised')

    def query(self, raw_line: str, column_name: str = None) -> str:

        if column_name is None:
            column_name = self._output_column_name

        cursor = self.db_connection.cursor()
        query_query = f'SELECT {column_name} FROM {self._main_table_name} WHERE {self._key_column_name} = ?'
        cursor.execute(query_query, (raw_line,))
        query_results = cursor.fetchone()
        if query_results:
            html_parse = query_results[0]
            if AppConfig.deep_log_databases:
                logger.info(f'{self._database_name}:{self._database_name} Query for {raw_line} successful')
            return html_parse
        else:
            if AppConfig.deep_log_databases:
                logger.info(f'{self._database_name}:{raw_line} was not found in the {self._database_name} database')
            raise CustomExceptions.EntryNotFound

    def insert(self, raw_line: str, transmuted_data: Union[str, bytes], column_name: str = None) -> None:
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
            insert_query = f'INSERT INTO {self._main_table_name} ({self._key_column_name}, {column_name}) VALUES (?, ?)'
            cursor.execute(insert_query, (raw_line, transmuted_data))
            self.db_connection.commit()
            self.db_updated = True
            if AppConfig.deep_log_databases:
                logger.info(
                    f'{self._database_name}:Insert of {column_name} for line {raw_line} in {self._main_table_name} was successful')
        else:
            if AppConfig.deep_log_databases:
                logger.info(
                    f'{self._database_name}:Insert of {column_name} into {self._main_table_name} was skipped as line already existed')

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
            if AppConfig.deep_log_databases:
                logger.info(f'{self._database_name}:{raw_line} archived from {self._main_table_name}')
            self.db_updated = True
        else:
            if AppConfig.deep_log_databases:
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
        if AppConfig.deep_log_databases:
            logger.info(f'{self._database_name}:{self._archive_table_name} Cleared')

    def clear_main_table(self) -> None:
        cursor = self.db_connection.cursor()
        clear_main_query = f'DELETE FROM {self._main_table_name}'
        cursor.execute(clear_main_query)
        self.db_connection.commit()
        if AppConfig.deep_log_databases:
            logger.critical(f'MAIN TABLE in {self._database_name} has been cleared')
        self.db_updated = True

    def reset_database(self):
        self.clear_main_table()
        self.clear_archive()
        self.initialize_db_structure()
        if AppConfig.deep_log_databases:
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
    """ Remember that these methods do not always explicitly check if the operations are valid, for example, there is no
    explicit check if another version of a line exists in the db"""

    # intrinsic settings
    _database_name = 'jisho_parse_db'
    _instance = None
    _db_path = AppConfig.jisho_parse_db_path

    _main_table_name = 'jisho_parse'
    _archive_table_name = 'jisho_parse_archive'

    _key_column_name = 'raw_line'  # the column in which the unique string that was transmuted is stored
    _output_column_name = 'parsed_html'
    _db_structure = \
        [
            [_main_table_name, ['id', 'raw_line', 'parsed_html']],
            [_archive_table_name, ['id', 'raw_line', 'parsed_html']]
        ]
    _db_data_types = {
        'id': 'TEXT',
        'raw_line': 'TEXT',
        'parsed_html': 'TEXT'
    }

    _main_table_create_query = f'CREATE TABLE IF NOT EXISTS {_main_table_name} (id INTEGER PRIMARY KEY, {_key_column_name} TEXT, parsed_html TEXT)'
    _archive_table_create_query = f'CREATE TABLE IF NOT EXISTS {_archive_table_name} (id INTEGER PRIMARY KEY, {_key_column_name} TEXT, parsed_html TEXT)'

    # operational flags
    db_updated = False

    def __new__(cls, *args, **kwargs):
        """This class method ensures that only one instance of the class exists,
        but I'm not sure of the scope of that exclusivity"""
        if cls._instance is None:
            cls._instance = super(JishoParseDBM, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.db_connection = sqlite3.connect(self._db_path)
        self.cached_raw_lines_dict = self.update_cached_dict_of_raw_lines()
        if AppConfig.deep_log_databases:
            logger.info(f'An instance of {self._database_name} was initialized')


class TextToSpeechDBM(DBM):
    """ Remember that these methods do not always explicitly check if the operations are valid, for example, there is no
    explicit check if another version of a line exists in the db"""

    # intrinsic settings
    _database_name = 'je_tts'
    _instance = None
    _db_path = AppConfig.je_tts_db

    _main_table_name = 'je_tts'
    _archive_table_name = 'je_tts_archive'

    _key_column_name = 'raw_line'
    _output_column_name = 'tts_bytes'
    _db_structure = \
        [
            [_main_table_name, ['id', _key_column_name, 'tts_bytes']],
            [_archive_table_name, ['id', _key_column_name, 'tts_bytes']]
        ]
    _db_data_types = {
        'id': 'TEXT',
        'raw_line': 'TEXT',
        'tts_bytes': 'BLOB'
    }

    _main_table_create_query = f'CREATE TABLE IF NOT EXISTS {_main_table_name} (id INTEGER PRIMARY KEY, {_key_column_name} TEXT, tts_bytes BLOB)'
    _archive_table_create_query = f'CREATE TABLE IF NOT EXISTS {_archive_table_name} (id INTEGER PRIMARY KEY, {_key_column_name} TEXT, tts_bytes BLOB)'

    # operational flags
    db_updated = False

    def __new__(cls, *args, **kwargs):
        """This class method ensures that only one instance of the class exists,
        but I'm not sure of the scope of that exclusivity"""
        if cls._instance is None:
            cls._instance = super(TextToSpeechDBM, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.db_connection = sqlite3.connect(self._db_path)
        # self.initialize_db_structure()
        self.cached_raw_lines_dict = self.update_cached_dict_of_raw_lines()
        if AppConfig.deep_log_databases:
            logger.info(f'An instance of {self._database_name} was initialized')


class TranslationDBM(DBM):
    """ Remember that these methods do not always explicitly check if the operations are valid, for example, there is no
    explicit check if another version of a line exists in the db"""

    # intrinsic settings
    _database_name = 'translations_db'
    _instance = None
    _db_path = AppConfig.translations_db_path

    _main_table_name = 'translations'
    _archive_table_name = 'translations_archive'

    _key_column_name = 'raw_line'  # the column in which the unique string that was transmuted is stored
    _output_column_name = ''
    _db_structure = \
        [
            [_main_table_name, ['id', _key_column_name, 'preprocessed', 'deepl_tl', 'google_tl', 'gpt_analysis']],
            [_archive_table_name, ['id', _key_column_name, 'preprocessed', 'deepl_tl', 'google_tl', 'gpt_analysis']]
        ]
    _db_data_types = {
        'id': 'TEXT',
        'raw_line': 'TEXT',
        'preprocessed': 'TEXT',
        'deepl_tl': 'TEXT',
        'google_tl': 'TEXT',
        'gpt_analysis': 'TEXT'
    }

    _main_table_create_query = f'CREATE TABLE IF NOT EXISTS {_main_table_name} (id INTEGER PRIMARY KEY, {_key_column_name} TEXT, preprocessed TEXT, deepl_tl TEXT, google_tl TEXT, gpt_analysis TEXT)'
    _archive_table_create_query = f'CREATE TABLE IF NOT EXISTS {_archive_table_name} (id INTEGER PRIMARY KEY, {_key_column_name} TEXT, preprocessed TEXT, deepl_tl TEXT, google_tl TEXT, gpt_analysis TEXT)'

    # operational flags
    db_updated = False

    def __new__(cls, *args, **kwargs):
        """This class method ensures that only one instance of the class exists,
        but I'm not sure of the scope of that exclusivity"""
        if cls._instance is None:
            cls._instance = super(TranslationDBM, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.db_connection = sqlite3.connect(self._db_path)
        self.cached_raw_lines_dict = self.update_cached_dict_of_raw_lines()
        if AppConfig.deep_log_databases:
            logger.info(f'An instance of {self._database_name} was initialized')
