from collections.abc import Callable
from loguru import logger
import asyncio
import concurrent.futures
import time
from typing import Union

from appconfig import AppConfig
from custom_dataclasses import RekaiText, Paragraph, Line
from transmutors import Transmute
from db_management import DBM, JishoParseDBM, TextToSpeechDBM, TranslationDBM
from custom_modules.utilities import log_process_time


class Process:
    @staticmethod
    @log_process_time
    def jisho_parse(rekai_text_object: RekaiText, parallel_process: bool = True) -> dict[str, str]:
        logger.info("Starting Jisho processing")

        list_of_strings_to_transmute = SubProcess.prepare_data(
            rekai_text_object=rekai_text_object,
            db_interface=JishoParseDBM(),
            preprocess=False,
            transmute_paragraphs=False,
            transmute_lines=True,
            transmute_clauses=False)

        list_of_transmuted_data_tuples = SubProcess.parallel_transmute(
            list_of_strings_to_transmute=list_of_strings_to_transmute,
            transmutor=Transmute.parse_string_with_jisho,
            max_workers=AppConfig.jisho_multipro_max_workers)

        SubProcess.update_database(
            list_of_transmuted_data_tuples=list_of_transmuted_data_tuples,
            db_interface=JishoParseDBM())

        logger.info("Finished Jisho processing")

        return

    @staticmethod
    @log_process_time
    def gcloud_tts(rekai_text_object: RekaiText, parallel_process: bool = True) -> dict[str, bytes]:
        logger.info("Starting Google Cloud TTS processing")

        list_of_strings_to_transmute = SubProcess.prepare_data(
            rekai_text_object=rekai_text_object,
            db_interface=TextToSpeechDBM(),
            preprocess=False,
            transmute_paragraphs=False,
            transmute_lines=True,
            transmute_clauses=False)

        list_of_transmuted_data_tuples = asyncio.run(SubProcess.async_transmute(
            list_of_strings_to_transmute=list_of_strings_to_transmute,
            transmutor=Transmute.tts_string_with_google_api))

        SubProcess.update_database(
            list_of_transmuted_data_tuples=list_of_transmuted_data_tuples,
            db_interface=TextToSpeechDBM())

        logger.info("Finished Google Cloud TTS processing")

        return



class SubProcess:

    @staticmethod
    def sync_transmute(
            list_of_strings_to_transmute: list,
            transmutor: Callable[[str], tuple[str, Union[str, bytes]]]) -> list[tuple[str,Union[str, bytes]]]:

        list_of_transmuted_data = [transmutor(string) for string in list_of_strings_to_transmute]

        return list_of_transmuted_data

    @staticmethod
    async def async_transmute(list_of_strings_to_transmute: list,
                              transmutor: Callable[[str], tuple[str, Union[str, bytes]]]) -> list[tuple[str, any]]:

        loop = asyncio.get_event_loop()

        async def async_func(transmutor, argument):
            return await loop.run_in_executor(None, transmutor, argument)

        tasks = [async_func(transmutor, string) for string in list_of_strings_to_transmute]
        list_of_transmuted_data = await asyncio.gather(*tasks)

        return list_of_transmuted_data

    @staticmethod
    def parallel_transmute(list_of_strings_to_transmute: list,
                           transmutor: Callable[[str], tuple[str, str]],
                           max_workers=AppConfig.general_multipro_max_workers) -> list[tuple[str, Union[str, bytes]]]:

        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            list_of_transmuted_data = list(executor.map(transmutor, list_of_strings_to_transmute))

        return list_of_transmuted_data

    @staticmethod
    def prepare_data(rekai_text_object: RekaiText,
                     db_interface: DBM,
                     preprocess: bool,
                     transmute_paragraphs: bool = False,
                     transmute_lines: bool = True,
                     transmute_clauses: bool = False) -> list[str]:

        dict_of_keystrings_in_db = db_interface.get_dict_of_keystrings_in_db()

        list_of_strings_for_transmutation = []

        # Extract parsable paragraphs in RekaiText Object
        list_of_paragraph_object_tuples: list[
            tuple[int, Paragraph]] = rekai_text_object.numbered_parsable_paragraph_objects

        # Conditionals for level of transmutation and check if already in database
        if transmute_paragraphs:
            for (_, paragraph_object) in list_of_paragraph_object_tuples:
                if preprocess:
                    if paragraph_object.preprocessed_text in dict_of_keystrings_in_db:
                        continue
                    else:
                        list_of_strings_for_transmutation.append(paragraph_object.preprocessed_text)
                else:
                    if paragraph_object.raw_text in dict_of_keystrings_in_db:
                        continue
                    else:
                        list_of_strings_for_transmutation.append(paragraph_object.raw_text)

        if transmute_lines:
            for (_, paragraph_object) in list_of_paragraph_object_tuples:
                list_of_line_objects_in_para = paragraph_object.numbered_line_objects
                for (_, line_object) in list_of_line_objects_in_para:
                    if preprocess:
                        if line_object.preprocessed_text in dict_of_keystrings_in_db:
                            continue
                        else:
                            list_of_strings_for_transmutation.append(line_object.preprocessed_text)
                    else:
                        if line_object.raw_text in dict_of_keystrings_in_db:
                            continue
                        else:
                            list_of_strings_for_transmutation.append(line_object.raw_text)

        if transmute_clauses:
            for (_, paragraph_object) in list_of_paragraph_object_tuples:
                list_of_line_objects_in_para = paragraph_object.numbered_line_objects
                for (_, line_object) in list_of_line_objects_in_para:
                    list_of_clause_objects_in_line = line_object.numbered_clause_objects
                    for (_, clause_object) in list_of_clause_objects_in_line:
                        if preprocess:
                            if clause_object.preprocessed_text in dict_of_keystrings_in_db:
                                continue
                            else:
                                list_of_strings_for_transmutation.append(clause_object.preprocessed_text)
                        else:
                            if clause_object.raw_text in dict_of_keystrings_in_db:
                                continue
                            else:
                                list_of_strings_for_transmutation.append(clause_object.raw_text)

        logger.info(f'Lines to transmute: {len(list_of_strings_for_transmutation)}')

        return list_of_strings_for_transmutation

    @staticmethod
    def update_database(list_of_transmuted_data_tuples: list, db_interface: DBM) -> None:

        for (raw_line, transmuted_data) in list_of_transmuted_data_tuples:
            db_interface.insert(raw_line=raw_line, transmuted_data=transmuted_data)
        db_interface.close_connection()
