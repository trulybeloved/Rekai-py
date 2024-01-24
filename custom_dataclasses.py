from dataclasses import dataclass
import json
from typing import Union
from loguru import logger

import nlp_modules.basic_nlp as BasicNLP
import nlp_modules.japanese_nlp as JNLP
from appconfig import AppConfig, RunConfig
from transmutors import Transmute
from db_management import DBM, JishoParseDBM, TextToSpeechDBM, DeepLDBM, GoogleTLDBM
from custom_modules.custom_exceptions import ClassificationError


class RekaiTextCommon:
    """UNDER CONSTRUCTON"""

    raw_text: str
    preprocessed_text: str

    # jisho_parse_html: str
    # tl_google: str
    # tl_deepl: str
    # gpt4_analysis: str

    db_interface: DBM

    def query_database(self, key: str, db_interface: DBM, column_name: Union[str, None] = None) -> Union[str, bytes]:
        result = db_interface.query(raw_line=key, column_name=column_name)
        return result


@dataclass
class Clause:
    # Instance Variables
    raw_text: str
    preprocessed_text: str
    # tl_google: str
    # tl_deepl: str

    def __init__(self, input_clause: str, input_prepro_clause: str):
        self.raw_text = input_clause
        self.preprocessed_text = input_prepro_clause

        if AppConfig.deep_log_dataclasses:
            logger.info(f'A new instance of {self.__class__.__name__} was initialized: {self.__class__.__repr__(self)}')


@dataclass
class Line:
    # Instance variables
    raw_text: str
    preprocessed_text: str
    # tl_google: str
    # tl_deepl: str
    # gpt4_analysis: str
    list_of_clauses: list
    clause_count: int
    numbered_clause_objects: list[tuple[int, Clause]]

    def __init__(self, input_line: str, input_prepro_line: Union[str, None]):

        self.raw_text = input_line
        self.list_of_clauses = JNLP.TextSplitter.regex_split_to_clauses(input_line)
        self.clause_count = len(self.list_of_clauses)

        if input_prepro_line:
            self.preprocessed_text = input_prepro_line
            list_of_preprocessed_lines = JNLP.TextSplitter.regex_split_to_clauses(self.preprocessed_text)
            self.generate_child_objects(Clause, string_list=self.list_of_clauses, prepro_string_list=list_of_preprocessed_lines)
        else:
            self.generate_child_objects(Clause, self.list_of_clauses, None)

        if AppConfig.deep_log_dataclasses:
            logger.info(f'A new instance of {self.__class__.__name__} was initialized: {self.__class__.__repr__(self)}')

    def is_single_clause(self) -> bool:
        """Checks if line has only one clause"""
        return not self.clause_count > 1

    def generate_child_objects(self, child_object, string_list: list, prepro_string_list: Union[list, None]):
        if prepro_string_list:
            self.numbered_clause_objects = [(index + 1, child_object(string, prepro_string)) for
                                          index, (string, prepro_string)
                                          in enumerate(zip(string_list, prepro_string_list))]
        else:
            self.numbered_clause_objects = [(index + 1, child_object(string, None)) for index, string in enumerate(string_list)]



@dataclass
class Paragraph:
    # Instance variables
    raw_text: str
    preprocessed_text: str
    list_of_raw_lines: list[str]
    line_count: int
    numbered_line_objects: list[tuple[int, Line]]
    unparsable: bool
    paragraph_type: str
    is_dialogue: bool = False
    is_narration: bool = False
    is_expression: bool = False

    def __init__(self, input_paragraph: str, input_prepro_para: Union[str, None]):
        # assert "\n" not in input_paragraph

        self.raw_text = input_paragraph
        self.list_of_raw_lines = JNLP.TextSplitter.regex_split_to_lines(input_paragraph)
        self.line_count = len(self.list_of_raw_lines)

        # check if the paragraph is unparsable
        # THIS FUNCTION IS PRESENTLY AN ARBITARY RULE THAT WORKS FOR MOST CASES NEEDS IMPROVEMENT
        self.unparsable = JNLP.Classifier.contains_no_parsable_ja_text(self.raw_text)

        if not self.unparsable:
            if input_prepro_para:
                self.preprocessed_text = input_prepro_para
                list_of_preprocessed_lines = JNLP.TextSplitter.regex_split_to_lines(self.preprocessed_text)
                self.generate_child_objects(Line, self.list_of_raw_lines, list_of_preprocessed_lines)
            else:
                self.generate_child_objects(Line, self.list_of_raw_lines, None)

        else:
            self.preprocessed_text = ''
            self.numbered_line_objects = []
            self.line_count = 0


        # PARAGRAPH CLASSIFIER GOES HERE
        if JNLP.Classifier.is_dialogue(self.raw_text) and not self.unparsable:
            self.paragraph_type = 'Dialogue'
            self.is_dialogue = True
        elif not self.unparsable:
            self.paragraph_type = 'Narration'
            self.is_narration = True
        elif self.unparsable:
            self.paragraph_type = 'Dialogue: Expressive'
            self.is_expression = True
        else:
            raise ClassificationError


        if AppConfig.deep_log_dataclasses:
            logger.info(f'A new instance of {self.__class__.__name__} was initialized: {self.__class__.__repr__(self)}')

    def is_single_line(self) -> bool:
        """Checks if paragraph has only one line"""
        return not self.line_count > 1

    def generate_child_objects(self, child_object, string_list: list, prepro_string_list: Union[list, None]):
        if prepro_string_list:
            self.numbered_line_objects = [(index + 1, child_object(string, prepro_string)) for
                                               index, (string, prepro_string)
                                               in enumerate(zip(string_list, prepro_string_list))]
        else:
            self.numbered_line_objects = [(index + 1, child_object(string, None)) for index, string in enumerate(string_list)]



@dataclass
class RekaiText:
    log_sink = logger.add(sink=AppConfig.dataclasses_log_path)

    # Instance variables (needed for dataclasses base methods to function)
    text_header: str
    raw_text: str
    preprocessed_text: str
    preprocessed_available: bool
    paragraph_count: int
    numbered_paragraph_objects: list[tuple[int, Paragraph]]
    numbered_parsable_paragraph_objects: list[tuple[int, Paragraph]]

    # Run configuration
    config_preprocess: bool
    config_run_jisho_parse: bool
    config_run_tts: bool

    def __init__(self, input_text: str, run_config_object: RunConfig, text_header: str,
                 input_preprocessed_text: str = None):
        # validation
        assert isinstance(input_text, str), f'Input text is not a valid string object'
        assert input_text != '', f'Input text is an empty string'
        assert isinstance(text_header, str), f'text_header is not a valid string object'

        # The run_configuration parameters pertaining to generation and processing can be sent along with the RekaiText
        # object.
        self.set_config(run_config_object)

        self.text_header = text_header

        self.raw_text = input_text

        paragraphs: list = BasicNLP.TextSplitter.splitlines_to_list(
            self.raw_text, keepends=False, strip_each_line=True, trim_list=True)

        self.paragraph_count = len(paragraphs)

        # Preprocessed text handling
        if self.config_preprocess:

            if input_preprocessed_text is not None:
                prepro_paragraphs = BasicNLP.TextSplitter.splitlines_to_list(
                    input_preprocessed_text, keepends=False, strip_each_line=True, trim_list=True)
                # check if the number of elements in prepro matches that in raw para list
                if len(paragraphs) == len(prepro_paragraphs):
                    self.preprocessed_text = input_preprocessed_text
                else:
                    logger.error(f'Provided preprocessed text failed to match with raw text. Using native preprocessor')

                    self.preprocessed_text = self.preprocess(input_string=self.raw_text)

                    prepro_paragraphs = BasicNLP.TextSplitter.splitlines_to_list(
                        self.preprocessed_text, keepends=False, strip_each_line=True, trim_list=True)

            else:
                logger.error(f'Provided preprocessed text failed to match with raw text. Using native preprocessor')

                self.preprocessed_text = self.preprocess(input_string=self.raw_text)

                prepro_paragraphs = BasicNLP.TextSplitter.splitlines_to_list(
                self.preprocessed_text, keepends=False, strip_each_line=True, trim_list=True)

            self.preprocessed_available = True
        else:
            self.preprocessed_text = ''
            self.preprocessed_available = False
            prepro_paragraphs = None

        # method below will set None to the propro arguments for all paragraph objects is prepro_lines is None
        self.generate_child_objects(Paragraph, paragraphs, prepro_paragraphs)

        self.numbered_parsable_paragraph_objects = self.get_parsable_paragraphs()

        if AppConfig.deep_log_dataclasses:
            logger.info(f'A new instance of {self.__class__.__name__} was initialized: {self.__class__.__repr__(self)}')

    def set_config(self, run_config_object: RunConfig):
        self.config_preprocess = run_config_object.preprocess
        self.config_run_jisho_parse = run_config_object.run_jisho_parse
        self.config_run_tts = run_config_object.run_tts

    def get_raw_paragraphs(self) -> list[str]:
        """Returns List of the raw text of all lines"""
        return [paragraph.raw_text for (_, paragraph) in self.numbered_paragraph_objects]

    def get_parsable_paragraphs(self) -> list[tuple[int, Paragraph]]:
        """Returns Numbered List of all lines that are parsable"""
        return list(filter(lambda e: not e[1].unparsable, self.numbered_paragraph_objects))

    def generate_child_objects(self, child_object, string_list: list, prepro_string_list: Union[list, None]):
        if prepro_string_list:
            self.numbered_paragraph_objects = [(index + 1, child_object(string, prepro_string)) for
                                               index, (string, prepro_string)
                                               in enumerate(zip(string_list, prepro_string_list))]
        else:
            self.numbered_paragraph_objects = [(index + 1, child_object(string, None)) for index, string in
                                               enumerate(string_list)]

    def preprocess(self, input_string: str):
        # Need to take file operations outside of this function into utilities
        path_to_replacements_json = AppConfig.path_to_replacements_json

        with open(path_to_replacements_json, 'r', encoding='utf-8') as file:
            replacements_dict = json.load(file)

        preprocessed_text = Transmute.preprocess_with_kairyou(
            input_string=input_string, input_replacements_dict=replacements_dict)
        return preprocessed_text
