from dataclasses import dataclass
from loguru import logger

import nlp_modules.basic_nlp as BasicNLP
import nlp_modules.japanese_nlp as JNLP
from appconfig import AppConfig


@dataclass
class Clause:
    # Instance Variables
    raw_text: str

    def __init__(self, input_clause: str):
        self.raw_text = input_clause

        if AppConfig.deep_log_dataclasses:
            logger.info(f'A new instance of {self.__class__.__name__} was initialized: {self.__class__.__repr__(self)}')


@dataclass
class Line:
    # Instance variables
    raw_text: str
    list_of_clauses: list
    clause_count: int
    numbered_clauses: list[tuple[int, Clause]]

    def __init__(self, input_line: str):
        self.raw_text = input_line
        self.list_of_clauses = JNLP.TextSplitter.split_line_to_list_of_clauses(input_line)
        self.clause_count = len(self.list_of_clauses)

        self.numbered_clauses = [(index + 1, Clause(clause)) for index, clause in enumerate(self.list_of_clauses)]

        if AppConfig.deep_log_dataclasses:
            logger.info(f'A new instance of {self.__class__.__name__} was initialized: {self.__class__.__repr__(self)}')

    def is_single_clause(self) -> bool:
        """Checks if line has only one clause"""
        return not self.clause_count > 1


@dataclass
class Paragraph:
    # Instance variables
    raw_text: str
    list_of_lines: list
    line_count: int
    numbered_lines: list[tuple[int, Line]]
    unparsable: bool
    paragraph_type: str

    def __init__(self, input_paragraph: str):
        # assert "\n" not in input_paragraph

        self.raw_text = input_paragraph
        self.list_of_lines = JNLP.TextSplitter.split_para_to_list_of_lines(input_paragraph)
        self.line_count = len(self.list_of_lines)

        self.numbered_lines = [(index + 1, Line(line)) for index, line in enumerate(self.list_of_lines)]

        # check if the paragraph is unparsable
        # THIS FUNCTION IS PRESENTLY AN ARBITARY RULE THAT WORKS FOR MOST CASES NEEDS IMPROVEMENT
        self.unparsable = JNLP.Classifier.contains_no_parsable_ja_text(self.raw_text)

        # PARAGRAPH CLASSIFIER GOES HERE
        self.paragraph_type = 'Unclassified'

        if AppConfig.deep_log_dataclasses:
            logger.info(f'A new instance of {self.__class__.__name__} was initialized: {self.__class__.__repr__(self)}')

    def is_single_line(self) -> bool:
        """Checks if paragraph has only one line"""
        return not self.line_count > 1


@dataclass
class RekaiText:

    log_sink = logger.add(sink=AppConfig.dataclasses_log_path)

    # Instance variables (needed for dataclasses base methods to function)
    raw_text: str
    text_header: str
    paragraph_count: int
    numbered_paragraphs: list[tuple[int, Paragraph]]
    numbered_parsable_paragraphs: list[tuple[int, Paragraph]]

    def __init__(self, input_text: str, text_header: str = ''):
        # validation
        assert isinstance(input_text, str), f'Input text is not a valid string object'
        assert input_text != '', f'Input text is an empty string'
        assert isinstance(text_header, str), f'text_header is not a valid string object'

        self.raw_text: str = input_text
        self.text_header: str = text_header
        paragraphs: list = BasicNLP.TextSplitter.splitlines_to_list(
            self.raw_text, keepends=False, strip_each_line=True, trim_list=True)

        self.paragraph_count = len(paragraphs)
        self.numbered_paragraphs = [(index + 1, Paragraph(para)) for index, para in enumerate(paragraphs)]
        self.numbered_parsable_paragraphs = self.get_parsable_paragraphs()

        if AppConfig.deep_log_dataclasses:
            logger.info(f'A new instance of {self.__class__.__name__} was initialized: {self.__class__.__repr__(self)}')

    def get_raw_paragraphs(self) -> list[str]:
        """Returns List of the raw text of all paragraphs"""
        return [paragraph.raw_text for (_, paragraph) in self.numbered_paragraphs]

    def get_parsable_paragraphs(self) -> list[tuple[int, Paragraph]]:
        """Returns Numbered List of all paragraphs that are parsable"""
        return list(filter(lambda e: not e[1].unparsable, self.numbered_paragraphs))
