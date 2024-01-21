from loguru import logger

from db_management import JishoParseDBM, TextToSpeechDBM, DeepLDBM, GoogleTLDBM
from custom_modules.custom_exceptions import EntryNotFound



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
            tts_bytes = db_interface.query(raw_line=raw_line)
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


import base64

def blob_to_base64(blob_data):
    # Encode the binary data to base64
    base64_data = base64.b64encode(blob_data).decode('utf-8')
    return base64_data

# Example usage:
# Assuming you have a Blob, you can read its binary data and pass it to the function

# Replace `your_blob_data` with the actual binary data of your Blob
your_blob_data = Fetch.tts_bytes(raw_line='戦いの余波にひび割れ、めくれ上がった街路にどっかりと乗せた足裏から伝わってくる活力を魂にみなぎらせ、正面、上空、翼を広げる威容を真っ向から睨んだ。')

base64_result = blob_to_base64(your_blob_data)
print(base64_result)
