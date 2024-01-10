import sqlite3
from appconfig import AppConfig
from custom_modules.custom_exceptions import CustomExceptions
from loguru import logger

# TODO


class JishoParseDBM:
    """ Remember that these methods do not always explicitly check if the operations are valid, for example, there is no
    explicit check if another version of a line exists in the db"""

    # intrinsic settings
    _database_name = 'jisho_parse_db'
    _instance = None
    _db_path = AppConfig.jisho_parse_db_path
    _main_table_name = 'jisho_parse'
    _archive_table_name = 'jisho_parse_archive'
    _db_structure = \
        [
            [_main_table_name, ['id', 'raw_line', 'parsed_html']],
            [_archive_table_name, ['id', 'raw_line', 'parsed_html']]
        ]

    # logging
    logger.add(sink=AppConfig.db_log_path)

    # operational flags
    db_updated = False

    @property
    def db_path(self):
        return self._db_path

    def __new__(cls, *args, **kwargs):
        """This class method ensures that only one instance of the class exists,
        but I'm not sure of the scope of that exclusivity"""
        if cls._instance is None:
            cls._instance = super(JishoParseDBM, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.db_connection = sqlite3.connect(self._db_path)
        self.cached_raw_lines_dict = self.update_cached_dict_of_raw_lines()
        logger.info(f'An instance of {self._database_name} db interface class was initialized')

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

    def initialize_db_stucture(self) -> None:
        structure_test = self.check_db_structure()
        if structure_test is True:
            logger.info(f'{self._database_name} is already initialized and has the correct structure.')
        else:
            try:
                cursor = self.db_connection.cursor()
                create_query = (f'CREATE TABLE IF NOT EXISTS {self._main_table_name} '
                                f'(id INTEGER PRIMARY KEY, raw_line TEXT, parsed_html TEXT)')
                cursor.execute(create_query)
                create_query = (f'CREATE TABLE IF NOT EXISTS {self._archive_table_name} '
                                f'(id INTEGER PRIMARY KEY, raw_line TEXT, parsed_html TEXT)')
                cursor.execute(create_query)
                logger.info(
                    f'{self._database_name}:{self._main_table_name} created. {self._archive_table_name} created. DB initialized')
                self.db_connection.commit()
                self.db_updated = True
            except Exception as e:
                logger.error(f'{self._database_name}:An Exception:{e} was raised')

    def update_cached_dict_of_raw_lines(self) -> dict:
        cursor = self.db_connection.cursor()
        list_query = f'SELECT raw_line from {self._main_table_name}'
        cursor.execute(list_query)
        list_of_raw_lines_in_db = [row[0] for row in cursor.fetchall()]
        list_of_placeholder_values = [None for item in list_of_raw_lines_in_db]
        dict_of_raw_lines_in_db = {key: value for key, value in
                                   zip(list_of_raw_lines_in_db, list_of_placeholder_values)}
        return dict_of_raw_lines_in_db

    def query(self, raw_line: str) -> str:
        cursor = self.db_connection.cursor()
        query_query = f'SELECT parsed_html FROM {self._main_table_name} WHERE raw_line = ?'
        cursor.execute(query_query, (raw_line,))
        query_results = cursor.fetchone()
        if query_results:
            html_parse = query_results[0]
            logger.info(f'{self._database_name}:{self._database_name} Query for {raw_line} successful')
            return html_parse
        else:
            logger.info(f'{self._database_name}:{raw_line} was not found in the {self._database_name} database')
            raise CustomExceptions.EntryNotFound

    def insert(self, raw_line: str, parsed_html: str) -> None:
        cursor = self.db_connection.cursor()
        # Check if raw_line already exists in the table
        # COUNT FUNCTION returns an integer with the total number of matching rows
        check_query = f'SELECT COUNT(*) FROM {self._main_table_name} WHERE raw_line = ?'
        cursor.execute(check_query, (raw_line,))
        count = cursor.fetchone()[0]
        if count == 0:
            # raw_line doesn't exist, so perform the insertion
            insert_query = f'INSERT INTO {self._main_table_name} (raw_line, parsed_html) VALUES (?, ?)'
            cursor.execute(insert_query, (raw_line, parsed_html))
            self.db_connection.commit()
            self.db_updated = True
            logger.info(
                f'{self._database_name}:Insert of parsed html for line {raw_line} in {self._main_table_name} was sucessful')
        else:
            logger.info(
                f'{self._database_name}:Insert of {raw_line} into {self._main_table_name} was skipped as line already existed')

    def archive(self, raw_line: str) -> None:
        cursor = self.db_connection.cursor()
        check_query = f'SELECT COUNT(*) FROM {self._main_table_name} WHERE raw_line = ?'
        cursor.execute(check_query, (raw_line,))
        count = cursor.fetchone()[0]
        if count != 0:
            archival_query = f'INSERT INTO {self._archive_table_name} (raw_line, parsed_html) '
            f'SELECT raw_line, parsed_html FROM {self._main_table_name} WHERE raw_line = ?'
            cursor.execute(archival_query, (raw_line,))
            delete_query = f'DELETE FROM {self._main_table_name} WHERE raw_line = ?'
            cursor.execute(delete_query, (raw_line,))
            self.db_connection.commit()
            logger.info(f'{self._database_name}:{raw_line} archived from {self._main_table_name}')
            self.db_updated = True
        else:
            logger.info(f'{self._database_name}:CHECK QUERY for {raw_line} in {self._database_name} failed. '
                        f'No such entry exists. Archive function is not applicable')

    def clear_archive(self) -> None:
        cursor = self.db_connection.cursor()
        clear_query = f'DELETE FROM {self._archive_table_name}'
        cursor.execute(clear_query)
        self.db_connection.commit()
        logger.info(f'{self._database_name}:{self._archive_table_name} Cleared')

    def clear_main_table(self) -> None:
        cursor = self.db_connection.cursor()
        clear_main_query = f'DELETE FROM {self._main_table_name}'
        cursor.execute(clear_main_query)
        self.db_connection.commit()
        logger.critical(f'MAIN TABLE in {self._database_name} has been cleared')
        self.db_updated = True

    def reset_database(self):
        self.clear_main_table()
        self.clear_archive()
        self.initialize_db_stucture()
        logger.critical(f'{self._database_name} has been wiped and reset')

    def get_raw_lines_dict(self) -> dict:
        if self.db_updated:
            self.update_cached_dict_of_raw_lines()
            self.db_updated = False
            return self.cached_raw_lines_dict
        else:
            return self.cached_raw_lines_dict

    def close_connection(self) -> None:
        self.db_connection.close()


class TextToSpeechDBM:
    """ Remember that these methods do not always explicitly check if the operations are valid, for example, there is no
    explicit check if another version of a line exists in the db"""

    # intrinsic settings
    _database_name = ('je_tts')
    _instance = None
    _db_path = AppConfig.je_tts_db
    _main_table_name = 'je_tts'
    _archive_table_name = 'je_tts_archive'
    _db_structure = \
        [
            [_main_table_name, ['id', 'raw_line', 'tts_bytes']],
            [_archive_table_name, ['id', 'raw_line', 'tts_bytes']]
        ]

    # logging
    logger.add(sink=AppConfig.db_log_path)

    # operational flags
    db_updated = False

    @property
    def db_path(self):
        return self._db_path

    def __new__(cls, *args, **kwargs):
        """This class method ensures that only one instance of the class exists,
        but I'm not sure of the scope of that exclusivity"""
        if cls._instance is None:
            cls._instance = super(TextToSpeechDBM, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self.db_connection = sqlite3.connect(self._db_path)
        # self.initialize_db_stucture()
        self.cached_raw_lines_dict = self.update_cached_dict_of_raw_lines()
        logger.info(f'An instance of {self._database_name} db interface class was initialized')

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
            logger.error(f'{self._database_name}: An Exception:{e} was raised')
            return False

    def initialize_db_stucture(self) -> None:
        structure_test = self.check_db_structure()
        if structure_test is True:
            logger.info(f'{self._database_name} is already initialized and has the correct structure.')
        else:
            try:
                cursor = self.db_connection.cursor()
                create_query = (f'CREATE TABLE IF NOT EXISTS {self._main_table_name} (id INTEGER PRIMARY KEY, '
                                f'raw_line TEXT, tts_bytes BLOB)')
                cursor.execute(create_query)
                create_query = (f'CREATE TABLE IF NOT EXISTS {self._archive_table_name} (id INTEGER PRIMARY KEY, '
                                f'raw_line TEXT, tts_bytes BLOB)')
                cursor.execute(create_query)
                logger.info(
                    f'{self._database_name}: {self._main_table_name} created. {self._archive_table_name} created. DB initialized')
                self.db_connection.commit()
                self.db_updated = True
            except Exception as e:
                logger.error(f'{self._database_name}:An Exception:{e} was raised')

    def update_cached_dict_of_raw_lines(self) -> dict:
        cursor = self.db_connection.cursor()
        list_query = f'SELECT raw_line from {self._main_table_name}'
        cursor.execute(list_query)
        list_of_raw_lines_in_db = [row[0] for row in cursor.fetchall()]
        list_of_placeholder_values = [None for item in list_of_raw_lines_in_db]
        dict_of_raw_lines_in_db = {key: value for key, value in
                                   zip(list_of_raw_lines_in_db, list_of_placeholder_values)}
        return dict_of_raw_lines_in_db

    def query(self, raw_line: str) -> bytes:
        cursor = self.db_connection.cursor()
        query_query = f'SELECT tts_bytes FROM {self._main_table_name} WHERE raw_line = ?'
        cursor.execute(query_query, (raw_line,))
        query_results = cursor.fetchone()
        if query_results:
            tts_bytes = query_results[0]
            logger.info(f'{self._database_name} Query for {raw_line} successful')
            return tts_bytes
        else:
            logger.info(f'{raw_line} was not found in the {self._database_name} database')
            raise CustomExceptions.EntryNotFound

    def insert(self, raw_line: str, tts_bytes: bytes) -> None:
        cursor = self.db_connection.cursor()
        # Check if raw_line already exists in the table
        # COUNT FUNCTION returns an integer with the total number of matching rows
        check_query = f'SELECT COUNT(*) FROM {self._main_table_name} WHERE raw_line = ?'
        cursor.execute(check_query, (raw_line,))
        count = cursor.fetchone()[0]
        if count == 0:
            # raw_line doesn't exist, so perform the insertion
            insert_query = f'INSERT INTO {self._main_table_name} (raw_line, tts_bytes) VALUES (?, ?)'
            cursor.execute(insert_query, (raw_line, sqlite3.Binary(tts_bytes)))
            self.db_connection.commit()
            self.db_updated = True
            logger.info(
                f'{self._database_name}:Insert of tts bytes for line {raw_line} in {self._main_table_name} was sucessful')

        else:
            logger.info(f'Insert of {raw_line} into {self._main_table_name} was skipped as line already existed')

    def archive(self, raw_line: str) -> None:
        cursor = self.db_connection.cursor()
        check_query = f'SELECT COUNT(*) FROM {self._main_table_name} WHERE raw_line = ?'
        cursor.execute(check_query, (raw_line,))
        count = cursor.fetchone()[0]
        if count != 0:
            archival_query = (f'INSERT INTO {self._archive_table_name} (raw_line, tts_bytes) SELECT raw_line, '
                              f'tts_bytes FROM {self._main_table_name} WHERE raw_line = ?')
            cursor.execute(archival_query, (raw_line,))
            delete_query = f'DELETE FROM {self._main_table_name} WHERE raw_line = ?'
            cursor.execute(delete_query, (raw_line,))
            self.db_connection.commit()
            logger.info(f'{self._database_name}:{raw_line} archived from {self._main_table_name}')
            self.db_updated = True
        else:
            logger.info(
                f'{self._database_name}:CHECK QUERY for {raw_line} in {self._database_name} failed. No such entry exists. Archive '
                f'function is not applicable')

    def clear_archive(self) -> None:
        cursor = self.db_connection.cursor()
        clear_query = f'DELETE FROM {self._archive_table_name}'
        cursor.execute(clear_query)
        self.db_connection.commit()
        logger.info(f'{self._database_name}:{self._archive_table_name} Cleared')

    def clear_main_table(self) -> None:
        cursor = self.db_connection.cursor()
        clear_main_query = f'DELETE FROM {self._main_table_name}'
        cursor.execute(clear_main_query)
        self.db_connection.commit()
        logger.critical(f'MAIN TABLE in {self._database_name} has been cleared')
        self.db_updated = True

    def reset_database(self):
        self.clear_main_table()
        self.clear_archive()
        self.initialize_db_stucture()
        logger.critical(f'{self._database_name} has been wiped and reset')

    def get_raw_lines_dict(self) -> dict:
        if self.db_updated:
            self.update_cached_dict_of_raw_lines()
            self.db_updated = False
            return self.cached_raw_lines_dict
        else:
            return self.cached_raw_lines_dict

    def close_connection(self) -> None:
        self.db_connection.close()
