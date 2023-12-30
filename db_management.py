import sqlite3
from os import path
from abc import ABC, abstractmethod
from Rekai.appconfig import AppConfig
from loguru import logger


datastores_path = path.abspath('./datastores')
# print(datastores_path)

class JishoParseDBM:
    ''' Remember that these methods do not always explicitly check if the operations are valid, for example, there is no
    explicit check if another version of a line exists in the db'''

    _instance = None
    _db_path = AppConfig.jisho_parse_db_path
    _main_table_name = 'jisho_parse'
    logger.add(sink='db_log.log')

    # operational flags
    db_updated = False

    @property
    def db_path(self):
        return self._db_path

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(JishoParseDBM, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.db_connection = sqlite3.connect(self._db_path)
        self.cached_raw_lines_dict = self.update_cached_dict_of_raw_lines()

    def initialize_db_stucture(self) -> None:
        cursor = self.db_connection.cursor()
        cursor.execute(f'SELECT name FROM sqlite_master WHERE type="table" AND name="{self._main_table_name}"')
        table_exists = cursor.fetchone()
        if table_exists:
            logger.info(f'{self._main_table_name} is already present')
        else:
            create_query = f'CREATE TABLE IF NOT EXISTS jisho_parse (id INTEGER PRIMARY KEY, raw_line TEXT, parsed_html TEXT)'
            cursor.execute(create_query)
            logger.info(f'{self._main_table_name} created. DB initialized')
            self.db_connection.commit()
            self.db_updated = True

    def update_cached_dict_of_raw_lines(self) -> dict:
        cursor = self.db_connection.cursor()
        list_query = f'SELECT raw_line from {self._main_table_name}'
        cursor.execute(list_query)
        list_of_raw_lines_in_db = [row[0] for row in cursor.fetchall()]
        list_of_placeholder_values = [None for item in list_of_raw_lines_in_db]
        dict_of_raw_lines_in_db = {key: value for key, value in zip(list_of_raw_lines_in_db, list_of_placeholder_values)}
        return dict_of_raw_lines_in_db

    def query(self, raw_line: str) -> str:
        cursor = self.db_connection.cursor()
        query_query = f'SELECT parsed_html FROM {self._main_table_name} WHERE raw_line = ?'
        cursor.execute(query_query, (raw_line,))
        query_results = cursor.fetchone()
        if query_results:
            html_parse = query_results[0]
            logger.info(f'Query for {raw_line} successful')
            return html_parse
        else:
            logger.info(f'{raw_line} was not found in the database')
            return r'||NOT FOUND||'

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
            logger.info(f'Insert of parsed html for line {raw_line} in {self._main_table_name} was sucessful')
        else:
            logger.info(f'Insert of {raw_line} into {self._main_table_name} was skipped as line already existed')

    def delete(self, raw_line: str) -> None:
        cursor = self.db_connection.cursor()
        delete_query = f'DELETE FROM {self._main_table_name} WHERE raw_line = ?'
        cursor.execute(delete_query, (raw_line,))
        self.db_connection.commit()
        logger.info(f'{raw_line} deleted from {self._main_table_name}')
        self.db_updated = True

    def get_raw_lines_dict(self):
        if self.db_updated:
            self.update_cached_dict_of_raw_lines()
            self.db_updated = False
            return self.cached_raw_lines_dict
        else:
            return self.cached_raw_lines_dict

    def close_connection(self) -> None:
        self.db_connection.close()

