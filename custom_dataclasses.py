from dataclasses import dataclass
from loguru import logger

import nlp_modules.basic_nlp as BasicNLP
import nlp_modules.japanese_nlp as JNLP
from Rekai.appconfig import AppConfig

@dataclass
class Clauses:

    # Instance variables
    source_line: str
    list_of_clauses: list
    number_of_clauses: int

    def __init__(self, input_line):

        self.source_line = input_line
        self.list_of_clauses = JNLP.TextSplitter.split_line_to_list_of_clauses(input_line)
        self.number_of_clauses = len(self.list_of_clauses)
        if self.number_of_clauses > 1:
            self.single_clause = False
        else:
            self.single_clause = True

        if AppConfig.deep_log_dataclasses:
            logger.info(f'A new instance of {self.__class__.__name__} was initialized: {self.__class__.__repr__(self)}')

@dataclass
class Lines:

    # Instance variables
    source_paragraph: str
    list_of_lines: list
    number_of_lines: int
    list_of_clause_object_tuples: list[tuple[int, Clauses]]

    def __init__(self, input_paragraph):

        # assert "\n" not in input_paragraph

        self.source_paragraph = input_paragraph
        self.list_of_lines = JNLP.TextSplitter.split_para_to_list_of_lines(input_paragraph)
        self.number_of_lines = len(self.list_of_lines)
        self.list_of_clause_object_tuples = [(index + 1, Clauses(line)) for index, line in enumerate(self.list_of_lines)]

        if self.number_of_lines > 1:
            self.single_line = False
        else:
            self.single_line = True

        if AppConfig.deep_log_dataclasses:
            logger.info(f'A new instance of {self.__class__.__name__} was initialized: {self.__class__.__repr__(self)}')

@dataclass
class RekaiText:

    log_sink = logger.add(sink=AppConfig.dataclasses_log_path)

    # Instance variables (needed for dataclasses base methods to function)
    raw_text: str
    list_of_paragraph_tuples: list[tuple[int, str]]
    number_of_paragraphs: int
    list_of_line_object_tuples: list[tuple[int, Lines]]

    def __init__(self, input_text: str):

        # validation
        assert isinstance(input_text, str), f'Input text is not a valid string object'
        assert input_text != '', f'Input text is an empty string'

        self.raw_text: str = input_text
        paragraphs: list = BasicNLP.TextSplitter.splitlines_to_list(
            self.raw_text, keepends=False, strip_each_line=True, trim_list=True)

        self.list_of_paragraph_tuples: list[tuple[int, str]] = [(index + 1, para) for index, para in enumerate(paragraphs)]
        self.number_of_paragraphs: int = len(self.list_of_paragraph_tuples)
        self.list_of_line_object_tuples: list[tuple[int, Lines]] = [(index + 1, Lines(para)) for index, para in enumerate(paragraphs)]

        if AppConfig.deep_log_dataclasses:
            logger.info(f'A new instance of {self.__class__.__name__} was initialized: {self.__class__.__repr__(self)}')
