from loguru import logger

from Rekai.db_management import JishoParseDBM, TextToSpeechDBM
from Rekai.custom_modules.custom_exceptions import CustomExceptions


class Fetch:

    @staticmethod
    def jisho_parsed_html(raw_line: str) -> str:

        db_interface = JishoParseDBM()
        try:
            parsed_html = db_interface.query(raw_line=raw_line)
            return parsed_html
        except CustomExceptions.EntryNotFound as e:
            logger.exception(e)
            raise e

    @staticmethod
    def tts_bytes(raw_line: str) -> bytes:

        db_interface = TextToSpeechDBM()
        try:
            tts_bytes = db_interface.query(raw_line=raw_line)
            return tts_bytes
        except CustomExceptions.EntryNotFound as e:
            logger.exception(e)
            raise e
