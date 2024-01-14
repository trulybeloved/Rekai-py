from collections.abc import Callable
from loguru import logger
import asyncio
import time

from appconfig import AppConfig
from custom_dataclasses import RekaiText, Paragraph, Line
from transmutors import Transmute
from db_management import DBM, JishoParseDBM, TextToSpeechDBM, TranslationDBM

class Wrapper:
    @staticmethod
    async def async_process(async_function, list_of_arguments: list):
        async_loop = asyncio.get_event_loop()

        tasks = [async_loop.create_task(async_function(args)) for args in list_of_arguments]
        results = await asyncio.gather(*tasks)
        return results


class Process:
    @staticmethod
    def jisho_parse(input_rekai_text_object: RekaiText, parallel_process: bool = True) -> dict[str, str]:
        logger.info("Starting Jisho processing")
        result = Process.process_with(input_rekai_text_object, JishoParseDBM(), Transmute.parse_string_with_jisho)
        logger.info("Finished Jisho processing")
        return result
 
    @staticmethod
    def gcloud_tts(input_rekai_text_object: RekaiText, parallel_process: bool = True) -> dict[str, bytes]:
        logger.info("Starting Google Cloud TTS processing")
        result = Process.process_with(input_rekai_text_object, TextToSpeechDBM(), Transmute.tts_string_with_google_api)
        logger.info("Finished Google Cloud TTS processing")
        return result
    
    @staticmethod
    def deepl_tl(input_rekai_text_object: RekaiText, parallel_process: bool = True) -> dict[str, str]:
        logger.info("Starting DeepL processing")
        result = Process.process_with(input_rekai_text_object, TranslationDBM(), Transmute.translate_string_with_deepl_api)
        logger.info("Finished DeepL processing")
        return result
    

# TODO: create parallelised process_with alternative.
    @staticmethod
    def process_with(input_rekai_text_object: RekaiText, db_interface: DBM, transmutor: Callable[[str], tuple[str, str]]) -> dict:

        # Extract parsable paragraphs in RekaiText Object
        list_of_paragraph_object_tuples: list[
            tuple[int, Paragraph]] = input_rekai_text_object.numbered_parsable_paragraphs

        list_of_lines_for_transmutation = []
        all_processed_lines = dict()

        # Check if already in database
        for (_, paragraph_object) in list_of_paragraph_object_tuples:
            list_of_lines: list = paragraph_object.list_of_raw_lines
            for line in list_of_lines:
                if line in db_interface.get_raw_lines_dict():
                    all_processed_lines[line] = db_interface.get_raw_lines_dict()[line]
                else:
                    list_of_lines_for_transmutation.append(line)

        logger.info(f'Lines to transmute: {len(list_of_lines_for_transmutation)}')

        # Transmutation
        start_time = time.time()
        list_of_transmuted_lines = [transmutor(line) for line in
                                        list_of_lines_for_transmutation]
        end_time = time.time()
        logger.success(f'TIME TAKEN FOR API calls: {end_time - start_time}')


        # Database update
        for (raw_line, transmuted_data) in list_of_transmuted_lines:
            db_interface.insert(raw_line=raw_line, tts_bytes=transmuted_data)
        db_interface.close_connection()
        
        all_processed_lines.update(list_of_transmuted_lines)
        return all_processed_lines 
