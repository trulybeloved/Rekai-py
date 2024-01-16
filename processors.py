from loguru import logger
import asyncio
import time

from appconfig import AppConfig
from custom_dataclasses import RekaiText, Paragraph, Line
from transmutors import Transmute
from db_management import JishoParseDBM, TextToSpeechDBM, TranslationDBM

class Wrapper:
    @staticmethod
    async def async_process(async_function, list_of_arguments: list):
        async_loop = asyncio.get_event_loop()

        tasks = [async_loop.create_task(async_function(args)) for args in list_of_arguments]
        results = await asyncio.gather(*tasks)
        return results


class Process:

    @staticmethod
    def jisho_parse(input_rekai_text_object: RekaiText,  parallel_process: bool = True) -> None:

        db_interface = JishoParseDBM()
        function_name = 'Jisho Parser'  # for logging

        # Extract parsable paragraphs in RekaiText Object
        list_of_paragraph_object_tuples: list[tuple[int, Paragraph]] = input_rekai_text_object.numbered_parsable_paragraphs

        list_of_lines_for_transmutation = []

        # Check if already in database
        for (_, paragraph_object) in list_of_paragraph_object_tuples:
            list_of_lines: list = paragraph_object.list_of_lines
            for line in list_of_lines:
                if line in db_interface.get_raw_lines_dict():
                    continue
                else:
                    list_of_lines_for_transmutation.append(line)

        logger.info(f'{function_name} - Lines to transmute: {len(list_of_lines_for_transmutation)}')

        # Transmutation
        start_time = time.time()
        if parallel_process:
            list_of_transmuted_lines = Transmute.parse_list_with_jisho(list_of_lines_for_transmutation)
        else:
            list_of_transmuted_lines = [Transmute.parse_string_with_jisho(line) for line in list_of_lines_for_transmutation]
        end_time = time.time()
        logger.success(f'TIME TAKEN FOR {function_name} API calls: {end_time - start_time}')

        # Database update
        for (raw_line, transmuted_data) in list_of_transmuted_lines:
            db_interface.insert(raw_line=raw_line, transmuted_data=transmuted_data)
        db_interface.close_connection()

    @staticmethod
    def gcloud_tts(input_rekai_text_object: RekaiText, parallel_process: bool = True) -> None:

        db_interface = TextToSpeechDBM()
        function_name = 'Google Cloud TTS'  # for logging

        # Extract parsable paragraphs in RekaiText Object
        list_of_paragraph_object_tuples: list[tuple[int, Paragraph]] = input_rekai_text_object.numbered_parsable_paragraphs

        list_of_lines_for_transmutation = []

        # Check if already in database
        for (_, paragraph_object) in list_of_paragraph_object_tuples:
            list_of_lines: list = paragraph_object.list_of_lines
            for line in list_of_lines:
                if line in db_interface.get_raw_lines_dict():
                    continue
                else:
                    list_of_lines_for_transmutation.append(line)

        logger.info(f'{function_name} - Lines to transmute: {len(list_of_lines_for_transmutation)}')

        # Transmutation
        start_time = time.time()
        if parallel_process:
            list_of_transmuted_lines: list[tuple] = asyncio.run(Transmute.async_tts_list_with_google_api(list_of_lines_for_transmutation))
        else:
            list_of_transmuted_lines = [Transmute.tts_string_with_google_api(line) for line in list_of_lines_for_transmutation]
        end_time = time.time()
        logger.success(f'TIME TAKEN FOR {function_name} API calls: {end_time - start_time}')

        # Database update
        for (raw_line, transmuted_data) in list_of_transmuted_lines:
            db_interface.insert(raw_line=raw_line, transmuted_data=transmuted_data)
        db_interface.close_connection()

    @staticmethod
    def deepl_tl(input_rekai_text_object: RekaiText, parallel_process: bool = True) -> None:

        db_interface = TranslationDBM()
        function_name = 'DeepL Translation'  # for logging

        # Extract parsable paragraphs in RekaiText Object
        list_of_paragraph_object_tuples: list[
            tuple[int, Paragraph]] = input_rekai_text_object.numbered_parsable_paragraphs

        list_of_lines_for_transmutation = []

        # Check if already in database
        for (_, paragraph_object) in list_of_paragraph_object_tuples:
            list_of_lines: list = paragraph_object.list_of_lines
            for line in list_of_lines:
                if line in db_interface.get_raw_lines_dict():
                    continue
                else:
                    list_of_lines_for_transmutation.append(line)

        logger.info(f'{function_name} - Lines to transmute: {len(list_of_lines_for_transmutation)}')

        # Transmutation
        start_time = time.time()
        if parallel_process:
            list_of_transmuted_lines: list[tuple] = asyncio.run(
                Transmute.async_translate_list_with_deepl_api(list_of_lines_for_transmutation))
        else:
            list_of_transmuted_lines = [Transmute.translate_string_with_deepl_api(line) for line in
                                        list_of_lines_for_transmutation]
        end_time = time.time()
        logger.success(f'TIME TAKEN FOR {function_name} API calls: {end_time - start_time}')

        # Database update
        for (raw_line, transmuted_data) in list_of_transmuted_lines:
            db_interface.insert(raw_line=raw_line, transmuted_data=transmuted_data)
        db_interface.close_connection()
