from dataclasses import dataclass
from loguru import logger

import nlp_modules.basic_nlp as BasicNLP
import nlp_modules.japanese_nlp as JNLP
from appconfig import AppConfig


@dataclass
class Line:
    # Instance variables
    line_raw: str
    list_of_clauses: list
    number_of_clauses: int

    def __init__(self, input_line):

        self.line_raw = input_line
        self.list_of_clauses = JNLP.TextSplitter.split_line_to_list_of_clauses(input_line)
        self.number_of_clauses = len(self.list_of_clauses)
        if self.number_of_clauses > 1:
            self.single_clause = False
        else:
            self.single_clause = True

        if AppConfig.deep_log_dataclasses:
            logger.info(f'A new instance of {self.__class__.__name__} was initialized: {self.__class__.__repr__(self)}')


@dataclass
class Paragraph:
    # Instance variables
    paragraph_raw: str
    list_of_lines: list
    number_of_lines: int
    single_line: bool
    list_of_line_object_tuples: list[tuple[int, Line]]
    unparsable: bool
    paragraph_type: str

    def __init__(self, input_paragraph):

        # assert "\n" not in input_paragraph

        self.paragraph_raw = input_paragraph
        self.list_of_lines = JNLP.TextSplitter.split_para_to_list_of_lines(input_paragraph)
        self.number_of_lines = len(self.list_of_lines)

        # check if the paragraph has only one line
        if self.number_of_lines > 1:
            self.single_line = False
        else:
            self.single_line = True

        self.list_of_line_object_tuples = [(index + 1, Line(line)) for index, line in enumerate(self.list_of_lines)]

        # check if the paragraph is unparsable
        # THIS FUNCTION IS PRESENTLY AN ARBITARY RULE THAT WORKS FOR MOST CASES NEEDS IMPROVEMENT
        if JNLP.Classifier.contains_no_parsable_ja_text(self.paragraph_raw):
            self.unparsable = True
        else:
            self.unparsable = False

        # PARAGRAPH CLASSIFIER GOES HERE
        self.paragraph_type = 'Unclassified'

        if AppConfig.deep_log_dataclasses:
            logger.info(f'A new instance of {self.__class__.__name__} was initialized: {self.__class__.__repr__(self)}')


@dataclass
class RekaiText:
    log_sink = logger.add(sink=AppConfig.dataclasses_log_path)

    # Instance variables (needed for dataclasses base methods to function)
    raw_text: str
    text_header: str
    list_of_paragraph_tuples: list[tuple[int, str]]
    number_of_paragraphs: int
    list_of_paragraph_object_tuples: list[tuple[int, Paragraph]]
    list_of_parsable_paragraph_object_tuples: list[tuple[int, Paragraph]]

    def __init__(self, input_text: str, text_header: str = ''):
        # validation
        assert isinstance(input_text, str), f'Input text is not a valid string object'
        assert input_text != '', f'Input text is an empty string'
        assert isinstance(text_header, str), f'text_header is not a valid string object'

        self.raw_text: str = input_text
        self.text_header: str = text_header
        paragraphs: list = BasicNLP.TextSplitter.splitlines_to_list(
            self.raw_text, keepends=False, strip_each_line=True, trim_list=True)

        self.list_of_paragraph_tuples = [(index + 1, para) for index, para in enumerate(paragraphs)]
        self.number_of_paragraphs = len(self.list_of_paragraph_tuples)
        self.list_of_paragraph_object_tuples = [(index + 1, Paragraph(para)) for index, para in enumerate(paragraphs)]

        self.list_of_parsable_paragraph_object_tuples = [(int, paragraph_object) for (int, paragraph_object) in
                                                         self.list_of_paragraph_object_tuples if
                                                         paragraph_object.unparsable is False]

        if AppConfig.deep_log_dataclasses:
            logger.info(f'A new instance of {self.__class__.__name__} was initialized: {self.__class__.__repr__(self)}')
