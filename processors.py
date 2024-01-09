from loguru import logger
import time

from Rekai.custom_dataclasses import RekaiText, Paragraph, Line
from Rekai.transmutors import Transmute
from Rekai.db_management import JishoParseDBM, TextToSpeechDBM
from Rekai.misc.Scratch import chapter_1_raw_text, chapter_raw_2


class Process:

    jisho_parse_db_interface = JishoParseDBM()
    tts_db_interface = TextToSpeechDBM()

    @staticmethod
    def jisho_parse(input_rekai_text_object: RekaiText, db_interface: JishoParseDBM = jisho_parse_db_interface) -> None:

        function_name = 'Jisho Parser'  # for logging

        # Extract parsable paragraphs in RekaiText Object
        list_of_paragraph_object_tuples: list[tuple[int, Paragraph]] = input_rekai_text_object.list_of_parsable_paragraph_object_tuples

        list_of_lines_for_transmutation = []

        # Check if already in database
        for (index, paragraph_object) in list_of_paragraph_object_tuples:
            list_of_lines: list = paragraph_object.list_of_lines
            for line in list_of_lines:
                if line in db_interface.get_raw_lines_dict():
                    continue
                else:
                    list_of_lines_for_transmutation.append(line)

        logger.info(f'{function_name} - Lines to transmute: {len(list_of_lines_for_transmutation)}')

        # Transmutation
        list_of_transmuted_lines = Transmute.parse_list_with_jisho(list_of_lines_for_transmutation)

        # Database update
        for (raw_line, transmuted_data) in list_of_transmuted_lines:
            db_interface.insert(raw_line=raw_line, parsed_html=transmuted_data)
        db_interface.close_connection()

    @staticmethod
    def gcloud_tts(input_rekai_text_object: RekaiText, db_interface: TextToSpeechDBM = tts_db_interface) -> None:

        function_name = 'Google Cloud TTS'  # for logging

        # Extract parsable paragraphs in RekaiText Object
        list_of_paragraph_object_tuples: list[tuple[int, Paragraph]] = input_rekai_text_object.list_of_parsable_paragraph_object_tuples

        list_of_lines_for_transmutation = []

        # Check if already in database
        for (index, paragraph_object) in list_of_paragraph_object_tuples:
            list_of_lines: list = paragraph_object.list_of_lines
            for line in list_of_lines:
                if line in db_interface.get_raw_lines_dict():
                    continue
                else:
                    list_of_lines_for_transmutation.append(line)

        logger.info(f'{function_name} - Lines to transmute: {len(list_of_lines_for_transmutation)}')

        # Transmutation
        list_of_transmuted_lines: list[tuple] = Transmute.tts_list_with_google_api(list_of_lines_for_transmutation)

        # Database update
        for (raw_line, transmuted_data) in list_of_transmuted_lines:
            db_interface.insert(raw_line=raw_line, tts_bytes=transmuted_data)
        db_interface.close_connection()

# if __name__ == "__main__":
#
#     starttime = time.time()
#     text_object = RekaiText(chapter_raw_2)
#     Processor.jisho_parse(text_object)
#     Processor.gcloud_tts(text_object)
#
#
#     endtime = time.time()
#     print(f'Execution time: {endtime - starttime}')
