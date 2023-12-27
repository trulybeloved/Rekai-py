"""Functions related to basic NLP"""

import re
import string

test_text = """
――これは本気でマズイことになった。





　一文無しで途方に暮れながら、彼の心中はそんな一言で埋め尽くされていた。



「……」

「やっぱ、貨幣価値とかって全然違うんだよな……」



　群衆に紛れれば一瞬で見失いそうなほど凡庸な見た目だ。

　が、そんな彼を見る人々の視線には『珍奇』なものでも見るような不可解な色が濃い。
"""

test_text_2 = """
　無遠慮な視線の波にさらされて、少年は腕を組みながら納得するしかない。



「つまり、これはあれだな」



　指を鳴らし、自分の方を見る人々に鳴らした指を向けながら、



「――異世界召喚もの、ということらしい」



　目の前を、巨大なトカゲ風の生き物に引かれた馬車的な乗り物が横切っていった。
"""

class FundamentalPatterns:
    """
    Class of basic pattern recognition functions. Takes a string as input and returns a bool
    """

    @staticmethod
    def contains_only_whitespace(input_text: str) -> bool:
        set_of_whitespace_characters = set(string.whitespace)
        return all(character in set_of_whitespace_characters for character in input_text)

    @staticmethod
    def contains_only_digits(input_text: str) -> bool:
        set_of_digit_characters = set(string.digits)
        return all(character in set_of_digit_characters for character in input_text)

    @staticmethod
    def contains_only_punctuation(input_text: str) -> bool:
        set_of_punctuation_characters = set(string.punctuation)
        return all(character in set_of_punctuation_characters for character in input_text)


class TextSplitter:
    """
    Class of basic text splitting functions.
    """

    @staticmethod
    def splitlines_to_list(input_text: str, *, prefix: [str, None] = None, suffix: [str, None] = None,
                           keepends: bool = False, strip_each_line: bool = True, trim_list: bool = True) -> list:

        """
        Converts a block of text into a list of strings using \n or \r as delimiters

        Parameters and modifications:
            strip_each_line: If true, will apply the string.strip() method to each line,
            removing whitespace from the start and ends of a string

            trim_list: If true, will remove list elements that are purely whitespace.
            It will remove the \u3000 whitespace from start of paragraphs

            Post strip and trim:
            prefix: adds a string at the start of every line in the list
            suffix: adds a string at the end of every line in the list
        """

        list_of_lines = input_text.splitlines(keepends=keepends)

        if strip_each_line:
            list_of_lines = [line.strip() for line in list_of_lines]

        if trim_list:
            list_of_lines = [line for line in list_of_lines
                             if not FundamentalPatterns.contains_only_whitespace(line)]
        if prefix or suffix:
            list_of_lines = [f'{prefix}{line}{suffix}' for line in list_of_lines]

        return list_of_lines

    @staticmethod
    def split_at_delimiter(input_text: str, delimiter: str) -> str:
        """
        Function that will split text at a specified delimiter
        """



# print(TextSplitter.splitlines_to_list(input_text=test_text, keepends=False, trim_list=True, strip_each_line=False))

