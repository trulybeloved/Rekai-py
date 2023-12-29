# from dataclasses import dataclass


# from Scratch import chapter_1_raw_text
import nlp_modules.basic_nlp as BasicNLP
import nlp_modules.japanese_nlp as JNLP
from loguru import logger

# logger.add(sink='log.log')
#
# raw_text_chapter_arc = 1
# raw_text_chapter_number = 1
# raw_text_chapter_title = '第一章１　　『ギザ十は使えない』'
# raw_text_chapter_name = '『ギザ十は使えない』'
# raw_text_chapter_content = chapter_1_raw_text


# @dataclass
class ReZeroChapter:
    """
    # arc_number: int
    # chapter_number: int
    # chapter_raw_name: str
    # chapter_raw_text: str
    # chapter_type: str = 'Typical' | 'Special'
    # content_type: str = 'WebNovel' | 'LightNovel' | 'SideContent'

    # number_of_paragraphs: int = None
    # list_of_para_index_raw_tuples: list = None
    # list_of_para_index_line_raw_tuples: list = None
    # list_of_arc_chapter_para_index_line_raw_tuples: list = None

    """

    def __init__(self,
                 arc_number: int,
                 chapter_number: int,
                 chapter_raw_name: str,
                 chapter_raw_text: str,
                 chapter_type: str = 'Typical',
                 content_type: str = 'WebNovel'
                 ):

        # validation
        assert arc_number >= 0, f'Arc number cannot be a negative integer'
        assert chapter_number >= 0, f'Chapter number cannot be a negative integer'
        assert isinstance(chapter_raw_name, str), f'Chapter Raw Name is not a string.'
        assert isinstance(chapter_raw_text, str), f'Chapter Raw text is not a string.'
        assert len(chapter_raw_text) > 0, f'Chapter Raw text is empty.'
        assert isinstance(chapter_type, str), f'Chapter Raw text is not a string.'
        assert isinstance(content_type, str), f'Chapter Raw text is not a string.'

        # assignment and generation of core instance attributes
        self.arc_number = arc_number
        self.chapter_number = chapter_number
        self.raw_name = chapter_raw_name
        self.raw_text = chapter_raw_text
        self.chapter_type = chapter_type
        self.content_type = content_type

        logger.info(f'A new instance of {self.__class__.__name__} was initialized')

    def display_info(self):
        """Display information about the chapter."""
        print(f'{self.__class__.__name__}', )

        for attr, value in vars(self).items():
            print(f"{attr}: {value}", end='\n')

    def __repr__(self):
        """Return a string representation of the object."""
        attributes = '| '.join(f'{key} = {value}\n' for key, value in vars(self).items())
        return f'{self.__class__.__name__}({attributes})'

    def set_url(self, url):
        """Set the URL for the chapter."""
        self.url = url


    def extract_paragraphs(self):
        """Extract, Process and Count the number of paragraphs in the raw text."""

        if self.raw_text:
            paragraphs = BasicNLP.TextSplitter.splitlines_to_list(
                self.raw_text,
                keepends=False,
                strip_each_line=True,
                # This is the default. It will remove the \u3000 whitespace from start of paragraphs
                trim_list=True
            )
            self.number_of_paragraphs = len(paragraphs)
            self.list_of_paragraphs = paragraphs
            self.list_of_para_paratext_tuples = [(index+1, paratext) for index, paratext in enumerate(paragraphs)]
            self.list_of_para_line_linetext_tuples = []
            for (para, paratext) in self.list_of_para_paratext_tuples:
                lines = JNLP.TextSplitter.split_para_to_list_of_lines(
                    paratext,
                    strip_each_line=False,
                    trim_list=True  # IF FALSE AN EMPTY STRING IS ADDED TO THE END OF THE LIST BY THE SPLIT FUNCTION
                )
                for line_index, line in enumerate(lines):
                    para_line_linetext_tuple = (para, line_index+1, line)
                    self.list_of_para_line_linetext_tuples.append(para_line_linetext_tuple)

        else:
            logger.error('Paragraphs could not be extracted as raw_text is empty')

#
# chapter = ReZeroChapter(raw_text_chapter_arc, raw_text_chapter_number, raw_text_chapter_name,
#                         raw_text_chapter_content)
#
# chapter.extract_paragraphs()
#
# list_of_paragraphs = chapter.list_of_paragraphs
# list_of_index_para_tuples = chapter.list_of_para_paratext_tuples
# list_of_index_para_line_tuples = chapter.list_of_para_line_linetext_tuples


# rzchap = RZChapter(1, 1, "Chapter 1")
# chapter.display_info()
