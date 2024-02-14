## built-in libraries
from typing import Union

import json

## third-party libraries
from loguru import logger

## custom modules
import nlp_modules.basic_nlp as BasicNLP
import nlp_modules.japanese_nlp as JNLP
from appconfig import AppConfig, RunConfig
from dataclasses import dataclass, field
from transmutors import Transmute
from db_management import DBM

@dataclass
class ParaInfo:
    is_dialogue: bool
    is_narration: bool
    is_expression: bool
    is_single_line: bool

    def __init__(self, is_dialogue, is_narration, is_expression, is_single_line):
        self.is_dialogue = is_dialogue
        self.is_narration = is_narration
        self.is_expression = is_expression
        self.is_single_line = is_single_line

class RekaiTextCommon:
    """UNDER CONSTRUCTON"""

    def query_database(self, key: str, db_interface: DBM, column_name: Union[str, None] = None) -> Union[str, bytes]:
        result = db_interface.query(raw_line=key, column_name=column_name)
        return result

    def clean_post_split(self, input_string):

        if not input_string:
            return input_string

        opening_characters = {"\"", "「"}
        closing_characters = {"\"", "」"}

        if input_string[0] in opening_characters:
            output_string = input_string[1:]
        else:
            output_string = input_string

        if input_string[-1] in closing_characters:
            output_string = output_string[:-1]
        else:
            output_string = output_string

        return output_string



@dataclass
class Clause(RekaiTextCommon):
    # Instance Variables

    raw_text: str
    original_raw_text: str
    preprocessed_text: str
    original_preprocessed_text: str

    def __init__(self, input_clause: str, input_prepro_clause: Union[str, None], run_config: RunConfig, para_info: ParaInfo):
        self.run_config = run_config
        self.para_info = para_info

        self.raw_text = input_clause
        self.original_raw_text = input_clause
        self.preprocessed_text = input_prepro_clause
        self.original_preprocessed_text = input_prepro_clause

        if self.run_config.clean_post_split and para_info.is_dialogue:
            self.raw_text = self.clean_post_split(self.raw_text)
            self.preprocessed_text = self.clean_post_split(self.preprocessed_text)

        if AppConfig.deep_log_dataclasses:
            logger.info(f'A new instance of {self.__class__.__name__} was initialized: {self.__class__.__repr__(self)}')


@dataclass
class Line(RekaiTextCommon):
    # Instance variables
    # run_config: RunConfig
    # para_info: ParaInfo
    raw_text: str
    original_raw_text: str
    preprocessed_text: str
    original_preprocessed_text: str # to store the text that was received during instance creation, free from post processing
    # tl_google: str
    # tl_deepl: str
    # gpt4_analysis: str
    list_of_clauses: list
    clause_count: int
    numbered_clause_objects: list[tuple[int, Clause]]

    def __init__(self, input_line: str, input_prepro_line: Union[str, None], run_config: RunConfig, para_info: ParaInfo):
        self.run_config = run_config
        self.para_info = para_info

        self.raw_text = input_line
        self.original_raw_text = input_line

        if run_config.clean_post_split and (not para_info.is_single_line) and (not para_info.is_dialogue):
            self.raw_text = self.clean_post_split(self.raw_text)

        # It is input line that is sent for splitting as we don't want any cleaning to affect the split
        self.list_of_clauses = JNLP.TextSplitter.regex_split_to_clauses(self.original_raw_text)
        self.clause_count = len(self.list_of_clauses)

        if input_prepro_line:
            self.preprocessed_text = input_prepro_line
            self.original_preprocessed_text = input_prepro_line

            # If cleaning is enabled and para is not single line neither a dialogue
            if run_config.clean_post_split and (not para_info.is_single_line) and para_info.is_dialogue:
                self.preprocessed_text = self.clean_post_split(self.preprocessed_text)

            list_of_preprocessed_lines = JNLP.TextSplitter.regex_split_to_clauses(self.original_preprocessed_text)
            self.generate_child_objects(Clause, string_list=self.list_of_clauses, prepro_string_list=list_of_preprocessed_lines)
        else:
            self.generate_child_objects(Clause, self.list_of_clauses, None)
            self.preprocessed_text = ''
            self.original_preprocessed_text = ''

        if AppConfig.deep_log_dataclasses:
            logger.info(f'A new instance of {self.__class__.__name__} was initialized: {self.__class__.__repr__(self)}')

    def is_single_clause(self) -> bool:
        """Checks if line has only one clause"""
        return not self.clause_count > 1

    def generate_child_objects(self, child_class: type[Clause], string_list: list, prepro_string_list: Union[list, None]):
        if prepro_string_list:
            self.numbered_clause_objects = [(index + 1, child_class(string, prepro_string, self.run_config, self.para_info)) for
                                            index, (string, prepro_string)
                                            in enumerate(zip(string_list, prepro_string_list))]
        else:
            self.numbered_clause_objects = [(index + 1, child_class(string, None, self.run_config, self.para_info)) for index, string in enumerate(string_list)]



@dataclass
class Paragraph(RekaiTextCommon):
    # Instance variables
    # run_config: RunConfig
    # para_info: ParaInfo

    raw_text: str
    preprocessed_text: str
    list_of_raw_lines: list[str]
    line_count: int

    unparsable: bool
    paragraph_type: str

    numbered_line_objects: list[tuple[int, Line]]

    is_dialogue: bool = False
    is_narration: bool = False
    is_expression: bool = False


    def __init__(self, input_paragraph: str, input_prepro_para: Union[str, None], run_config: RunConfig):
        # assert "\n" not in input_paragraph

        self.run_config = run_config

        self.raw_text = input_paragraph

        self.list_of_raw_lines = JNLP.TextSplitter.regex_split_to_lines(input_paragraph)
        self.line_count = len(self.list_of_raw_lines)

        # check if the paragraph is unparsable
        # THIS FUNCTION IS PRESENTLY AN ARBITARY RULE THAT WORKS FOR MOST CASES NEEDS IMPROVEMENT
        self.unparsable = JNLP.Classifier.contains_no_parsable_ja_text(self.raw_text)

        # PARAGRAPH CLASSIFIER GOES HERE
        if JNLP.Classifier.is_dialogue(self.raw_text) and not self.unparsable:
            self.paragraph_type = 'Dialogue'
            self.is_dialogue = True
        elif not self.unparsable:
            self.paragraph_type = 'Narration'
            self.is_narration = True
        elif self.unparsable and JNLP.Classifier.is_dialogue(self.raw_text):
            self.paragraph_type = 'Dialogue: Expressive'
            self.is_expression = True
        else:
            self.paragraph_type = 'Unparsable/Division'

        self.para_info = ParaInfo(
            is_dialogue=self.is_dialogue,
            is_narration=self.is_narration,
            is_expression=self.is_expression,
            is_single_line=self.is_single_line()
        )

        # Split in the processing pipeline between parsable and unparsable paragraphs
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

        if AppConfig.deep_log_dataclasses:
            logger.info(f'A new instance of {self.__class__.__name__} was initialized: {self.__class__.__repr__(self)}')

    def is_single_line(self) -> bool:
        """Checks if paragraph has only one line"""
        return not self.line_count > 1

    def generate_child_objects(self, child_object: type[Line], string_list: list, prepro_string_list: Union[list, None]):
        if prepro_string_list:
            self.numbered_line_objects = [(index + 1, child_object(string, prepro_string, self.run_config, self.para_info)) for
                                               index, (string, prepro_string)
                                               in enumerate(zip(string_list, prepro_string_list))]
        else:
            self.numbered_line_objects = [(index + 1, child_object(string, None, self.run_config, self.para_info)) for index, string in
                                               enumerate(string_list)]

@dataclass
class RekaiText(RekaiTextCommon):

    run_config: RunConfig = field(repr=False)
    timestamp: int

    # Instance variables (needed for dataclasses base methods to function)
    text_header: str
    raw_text: str
    preprocessed_text: Union[str, None]
    preprocessed_available: bool
    paragraph_count: int
    numbered_paragraph_objects: list[tuple[int, Paragraph]]
    numbered_parsable_paragraph_objects: list[tuple[int, Paragraph]]

    # Run configuration
    config_preprocess: bool
    config_run_jisho_parse: bool
    config_run_tts: bool

    def __init__(self, input_text: str, run_config_object: RunConfig, text_header: str,
                 input_preprocessed_text: str):
        # validation
        assert isinstance(input_text, str), f'Input text is not a valid string object'
        assert input_text != '', f'Input text is an empty string'
        assert isinstance(text_header, str), f'text_header is not a valid string object'

        # The run_configuration parameters pertaining to generation and processing can be sent along with the RekaiText
        # object.
        self.run_config = run_config_object
        self.timestamp = run_config_object.run_timestamp
        self.config_preprocess = run_config_object.preprocess
        self.config_run_jisho_parse = run_config_object.run_jisho_parse
        self.config_run_tts = run_config_object.run_tts

        self.text_header = text_header

        self.raw_text = input_text

        paragraphs: list = BasicNLP.TextSplitter.splitlines_to_list(
            self.raw_text, keepends=False, strip_each_line=True, trim_list=True)

        self.paragraph_count = len(paragraphs)

        # Preprocessed text handling
        if self.config_preprocess:

            if input_preprocessed_text:
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
                logger.error(f'Preprocessed Text was not provided. Using native preprocessor')

                self.preprocessed_text = self.preprocess(input_string=self.raw_text)

                prepro_paragraphs = BasicNLP.TextSplitter.splitlines_to_list(
                    self.preprocessed_text, keepends=False, strip_each_line=True, trim_list=True)

            self.preprocessed_available = True
        else:
            self.preprocessed_text = None
            self.preprocessed_available = False
            prepro_paragraphs = None

        # method below will set None to the propro arguments for all paragraph objects is prepro_lines is None
        self.generate_child_objects(Paragraph, paragraphs, prepro_paragraphs, self.run_config)

        self.numbered_parsable_paragraph_objects = self.get_parsable_paragraphs()

        if AppConfig.deep_log_dataclasses:
            logger.info(f'A new instance of {self.__class__.__name__} was initialized: {self.__class__.__repr__(self)}')


    def get_raw_paragraphs(self) -> list[str]:
        """Returns List of the raw text of all lines"""
        return [paragraph.raw_text for (_, paragraph) in self.numbered_paragraph_objects]

    def get_parsable_paragraphs(self) -> list[tuple[int, Paragraph]]:
        """Returns Numbered List of all lines that are parsable"""
        return list(filter(lambda e: not e[1].unparsable, self.numbered_paragraph_objects))

    def generate_child_objects(self, child_class: type[Paragraph], string_list: list, prepro_string_list: Union[list, None], run_config: RunConfig):
        if prepro_string_list:
            self.numbered_paragraph_objects = [(index + 1, child_class(string, prepro_string, run_config)) for
                                               index, (string, prepro_string)
                                               in enumerate(zip(string_list, prepro_string_list))]
        else:
            self.numbered_paragraph_objects = [(index + 1, child_class(string, None, run_config)) for index, string in
                                               enumerate(string_list)]

    def preprocess(self, input_string: str):
        # Need to take file operations outside of this function into utilities
        path_to_replacements_json = AppConfig.path_to_replacements_json

        with open(path_to_replacements_json, 'r', encoding='utf-8') as file:
            replacements_dict = json.load(file)

        preprocessed_text = Transmute.preprocess_with_kairyou(
            input_string=input_string, input_replacements_dict=replacements_dict)
        return preprocessed_text
