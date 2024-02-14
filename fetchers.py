## third-party libraries
from loguru import logger

## custom modules
from db_management import JishoParseDBM, TextToSpeechDBM, DeepLDBM, GoogleTLDBM
from custom_modules.custom_exceptions import EntryNotFound
from custom_modules.utilities import decode_bytes_from_base64_string



class Fetch:

    @staticmethod
    def jisho_parsed_html(raw_line: str) -> str:

        db_interface = JishoParseDBM()
        try:
            parsed_html = db_interface.query(raw_line=raw_line)
            return parsed_html
        except EntryNotFound as e:
            logger.exception(e)
            raise e

    @staticmethod
    def tts_bytes(raw_line: str) -> bytes:

        db_interface = TextToSpeechDBM()
        try:
            base64_string = db_interface.query(raw_line=raw_line)
            tts_bytes = decode_bytes_from_base64_string(base64_string)

            return tts_bytes
        except EntryNotFound as e:
            logger.exception(e)
            raise e

    @staticmethod
    def deepl_tl(raw_line: str) -> bytes:

        db_interface = DeepLDBM()
        try:
            result = db_interface.query(raw_line=raw_line)
            return result
        except EntryNotFound as e:
            logger.exception(e)
            raise e

    @staticmethod
    def google_tl(raw_line: str) -> bytes:

        db_interface = GoogleTLDBM()
        try:
            result = db_interface.query(raw_line=raw_line)
            return result
        except EntryNotFound as e:
            logger.exception(e)
            raise e


