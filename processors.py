import math
from collections.abc import Callable
import asyncio
import concurrent.futures
from typing import Union
import functools

from loguru import logger

from appconfig import AppConfig
from custom_dataclasses import RekaiText, Paragraph
from transmutors import Transmute
from db_management import DBM, JishoParseDBM, TextToSpeechDBM, DeepLDBM, GoogleTLDBM
from custom_modules.utilities import ProgressMonitor


class Process:

    @staticmethod
    async def jisho_parse(rekai_text_object: RekaiText):
        logger.info("Starting Jisho processing")
        timestamp = rekai_text_object.timestamp

        list_of_strings_to_transmute = SubProcess.prepare_data(
            rekai_text_object=rekai_text_object,
            db_interface=JishoParseDBM(),
            preprocess=False,
            transmute_paragraphs=False,
            transmute_lines=True,
            transmute_clauses=False)

        if not list_of_strings_to_transmute:
            logger.info('No strings required transmutation. API calls were not made')
            return

        total_transmute_count = len(list_of_strings_to_transmute)
        logger.info(f'Jisho Parse - Number of strings for transmutation: {total_transmute_count}')
        progress_monitor = ProgressMonitor(task_name='Jisho Parse', total_task_count=total_transmute_count)

        if AppConfig.parallel_process:
            _ = await SubProcess.async_transmute(
                list_of_strings_to_transmute=list_of_strings_to_transmute,
                transmutor=Transmute.parse_string_with_jisho,
                timestamp=timestamp,
                progress_monitor=progress_monitor)

        else:
            SubProcess.sync_transmute(
                list_of_strings_to_transmute=list_of_strings_to_transmute,
                transmutor=Transmute.parse_string_with_jisho,
                timestamp=timestamp,
                progress_monitor=progress_monitor)

        logger.success("Finished Jisho processing")

        return

    @staticmethod
    async def gcloud_tts(rekai_text_object: RekaiText):
        logger.info("Starting Google Cloud TTS processing")
        timestamp = rekai_text_object.timestamp

        list_of_strings_to_transmute = SubProcess.prepare_data(
            rekai_text_object=rekai_text_object,
            db_interface=TextToSpeechDBM(),
            preprocess=False,
            transmute_paragraphs=False,
            transmute_lines=True,
            transmute_clauses=False)

        if not list_of_strings_to_transmute:
            logger.info('No strings required transmutation. API calls were not made')
            return

        total_transmute_count = len(list_of_strings_to_transmute)
        logger.info(f'GCloud TTS - Number of strings for transmutation: {total_transmute_count}')
        progress_monitor = ProgressMonitor(task_name='GCloud TTS', total_task_count=total_transmute_count)

        if AppConfig.parallel_process:
            _ = await SubProcess.async_transmute(
                list_of_strings_to_transmute=list_of_strings_to_transmute,
                transmutor=Transmute.tts_string_with_google_api,
                timestamp=timestamp,
                progress_monitor=progress_monitor)
        else:
            SubProcess.sync_transmute(
                list_of_strings_to_transmute=list_of_strings_to_transmute,
                transmutor=Transmute.tts_string_with_google_api,
                timestamp=timestamp,
                progress_monitor=progress_monitor)

        logger.success("Finished Google Cloud TTS processing")

        return

    @staticmethod
    async def deepl_tl(rekai_text_object: RekaiText):
        logger.info("Starting DeepL Translation")
        timestamp = rekai_text_object.timestamp

        list_of_strings_to_transmute = SubProcess.prepare_data(
            rekai_text_object=rekai_text_object,
            db_interface=DeepLDBM(),
            preprocess=rekai_text_object.run_config.use_preprocessed_for_deepl_tl,
            transmute_paragraphs=False,
            transmute_lines=True,
            transmute_clauses=True)

        if not list_of_strings_to_transmute:
            logger.info('No strings required transmutation. API calls were not made')
            return

        total_transmute_count = len(list_of_strings_to_transmute)
        logger.info(f'Deepl TL - Number of strings for transmutation: {total_transmute_count}')
        progress_monitor = ProgressMonitor(task_name='Deepl TL', total_task_count=total_transmute_count)

        if AppConfig.parallel_process:
            _ = await SubProcess.async_transmute(
                list_of_strings_to_transmute=list_of_strings_to_transmute,
                transmutor=Transmute.translate_string_with_deepl_api,
                timestamp=timestamp,
                progress_monitor=progress_monitor)
        else:
            SubProcess.sync_transmute(
                list_of_strings_to_transmute=list_of_strings_to_transmute,
                transmutor=Transmute.translate_string_with_deepl_api,
                timestamp=timestamp,
                progress_monitor=progress_monitor)

        logger.success('Finished DeepL Translation')

        return

    @staticmethod
    async def google_tl(rekai_text_object: RekaiText):
        """ THIS USES CHUNKED PROCESSING"""

        logger.info("Starting Google Translation")
        timestamp = rekai_text_object.timestamp

        list_of_strings_to_transmute = SubProcess.prepare_data(
            rekai_text_object=rekai_text_object,
            db_interface=GoogleTLDBM(),
            preprocess=rekai_text_object.run_config.use_preprocessed_for_google_tl,
            transmute_paragraphs=False,
            transmute_lines=True,
            transmute_clauses=True)

        if not list_of_strings_to_transmute:
            logger.info('No strings required transmutation. API calls were not made')
            return

        total_transmute_count = len(list_of_strings_to_transmute)
        logger.info(f'Google TL - Number of strings for transmutation: {total_transmute_count}')
        total_chunk_count = math.ceil((total_transmute_count / AppConfig.transmutor_chunk_size))

        progress_monitor = ProgressMonitor(task_name='Google TL', total_task_count=total_chunk_count)

        if AppConfig.parallel_process:
            await SubProcess.async_transmute_chunks(
                list_of_strings_to_transmute=list_of_strings_to_transmute,
                transmutor=Transmute.translate_chunk_with_google_tl_api,
                timestamp=timestamp,
                progress_monitor=progress_monitor)
        else:
            SubProcess.sync_transmute(
                list_of_strings_to_transmute=list_of_strings_to_transmute,
                transmutor=Transmute.translate_string_with_google_tl_api,
                timestamp=timestamp,
                progress_monitor=progress_monitor)

        logger.success('Finished Google Translation')

        return


class SubProcess:

    @staticmethod
    def sync_transmute(
            list_of_strings_to_transmute: list,
            transmutor: Callable[[str, int, ProgressMonitor, int, int], tuple[str, str]],
            timestamp: int,
            progress_monitor: ProgressMonitor) -> None:

        total_string_count = len(list_of_strings_to_transmute)

        list_of_transmuted_data = [transmutor(string, timestamp, progress_monitor, index+1, total_string_count) for
                                   index, string in enumerate(list_of_strings_to_transmute)]


    @staticmethod
    async def async_transmute(
            list_of_strings_to_transmute: list,
            transmutor: Callable[[str, int, ProgressMonitor, int, int], tuple[str, str]],
            timestamp: int,
            progress_monitor: ProgressMonitor) -> list:

        total_string_count = len(list_of_strings_to_transmute)

        loop = asyncio.get_event_loop()

        async def async_func(transmutor, *args):
            partial_transmutor = functools.partial(transmutor, *args)  # partial functions

            executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=AppConfig.general_multithread_max_workers)  # asyncio can run coroutines with other context managers like executors from concurrent.futures

            return await loop.run_in_executor(executor=None, func=partial_transmutor)

        tasks = [async_func(transmutor, string, timestamp, progress_monitor, index+1, total_string_count) for
                 index, string in enumerate(list_of_strings_to_transmute)]

        _ = await asyncio.gather(*tasks)

        return _


    @staticmethod
    async def async_transmute_chunks(
            list_of_strings_to_transmute: list,
            transmutor: Callable[[list, int, ProgressMonitor, int, int], tuple[str, str]],
            timestamp: int,
            progress_monitor: ProgressMonitor,
            chunk_size: int = AppConfig.transmutor_chunk_size) -> list:

        total_string_count = len(list_of_strings_to_transmute)

        loop = asyncio.get_event_loop()

        async def async_func(transmutor, *args):
            partial_transmutor = functools.partial(transmutor, *args)  # partial functions

            executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=AppConfig.general_multithread_max_workers)  # asyncio can run coroutines with other context managers like executors from concurrent.futures

            return await loop.run_in_executor(executor=None, func=partial_transmutor)

        list_of_chunks_to_transmute = [list_of_strings_to_transmute[i:i + chunk_size] for i in range(0, total_string_count, chunk_size)]

        total_chunk_count = len(list_of_strings_to_transmute)

        tasks = [async_func(transmutor, chunk, timestamp, progress_monitor, index+1, total_chunk_count) for
                 index, chunk in enumerate(list_of_chunks_to_transmute)]

        _ = await asyncio.gather(*tasks)

        return _


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

        # As single clause lines and single line paragraphs being included can possibly result in duplicates
        list_of_unique_strings_for_transmutation = list(set(list_of_strings_for_transmutation))

        if not all(list_of_unique_strings_for_transmutation):
            return []

        return list_of_unique_strings_for_transmutation

    @staticmethod
    def query_database(key: str, db_interface: DBM, column_name: Union[str, None] = None) -> Union[str, bytes]:

        result = db_interface.query(raw_line=key, column_name=column_name)
        return result
