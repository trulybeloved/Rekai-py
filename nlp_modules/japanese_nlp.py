"""Functions related to japanese NLP"""

import re

from bs4 import BeautifulSoup
from loguru import logger

from nlp_modules.patterns import Regex, Charsets
from nlp_modules.basic_nlp import FundamentalPatterns
from custom_modules.custom_exceptions import TextSplitError
from appconfig import AppConfig

class Classifier:

    @staticmethod
    def contains_no_parsable_ja_text(input_text: str) -> bool:
        """
        Checks if the given input text contains any parsable Japanese text.

        This method removes certain characters (expressions and punctuation) from
        the input text and performs further checks to determine if the remaining
        string is not parsable Japanese text.

        Args:
        - input_text (str): The text to be examined for parsable Japanese content.

        Returns:
        - bool: True if the input text does not contain parsable Japanese text,
                False otherwise.
        """

        replacement_set = Charsets.EXPRESSIONS | Charsets.PUNCTUATION
        for char in replacement_set:
            input_text = input_text.replace(char, '')

        # further checks on the remaining string
        same_kana_repeated = bool(re.match(Regex.same_hiragana_repeated, input_text))
        if same_kana_repeated:
            return True

        only_single_kana = bool(re.match(Regex.any_single_kana, input_text))
        if only_single_kana:
            return True

        # Needs an additional dictionary based check
        result = bool(len(input_text) < 1)
        return result

    @staticmethod
    def contains_no_kanji(input_text: str) -> bool:
        regex_pattern_for_any_kanji = re.compile(Regex.any_single_kanji, re.IGNORECASE)
        return not bool(regex_pattern_for_any_kanji.search(input_text))

    @staticmethod
    def is_dialogue(input_text: str) -> bool:
        """
        Checks if the given input text contains any patterns indicative of dialogue.

        This method uses regular expressions to identify potential dialogue patterns,
        such as text enclosed in single or double quotes. It returns True if any of
        these patterns are found in the input text, indicating the presence of dialogue.

        REGEX can be found in nlp_modules/patterns.py

        Args:
        - input_text (str): The text to be examined for dialogue patterns.

        Returns:
        - bool: True if any dialogue patterns are found, False otherwise.
        """

        regex_patterns_for_dialogues: list = [
            Regex.anything_bounded_by_single_quotes,
            Regex.anything_bounded_by_double_quotes,
            Regex.anything_bounded_by_multiple_single_quotes,
            Regex.anything_bounded_by_multiple_double_quotes
        ]

        re_objects_for_regex_patterns = [re.compile(pattern) for pattern in regex_patterns_for_dialogues]

        return any(re_object.search(input_text) for re_object in re_objects_for_regex_patterns)

class Extractor:
    @staticmethod
    def extract_kanji_block(input_text: str) -> tuple[str, str]:
        regex_pattern_for_kanji_block = re.compile(Regex.continuous_blocks_of_kanji)
        kanji_block_match = regex_pattern_for_kanji_block.match(input_text)
        kanji_block = kanji_block_match.group(0)
        non_kanji_block = input_text.replace(kanji_block, '')
        return kanji_block, non_kanji_block


class TextSplitter:

    @staticmethod
    def regex_split_to_lines(input_text: str) -> list:
        """
        Splits the input text into lines using a regular expression pattern for line detection.

        Args:
            input_text (str): The input text to be split into lines.

        Returns:
            list: A list of strings representing the lines extracted from the input text.

        The function uses a regular expression pattern defined in `Regex.pattern_for_line`
        to identify and extract lines from the input text. It handles cases where the regular
        expression might miss substrings by attempting to reassemble the paragraph and re-spliting it.
        The final result is a list of lines, with any leading or trailing whitespace removed.

        If debugging mode (`AppConfig.PREVENT_TRANSMUTE_IF_TEXT_PROCESSING_ERRORS`) is enabled,
        the function may set the `GLOBAL_RUN_STOP` flag in `AppConfig` on error. Otherwise, it
        logs a warning and considers the entire input text as a single line.

        Note:
        - Regex patterns are all defined in the Regex class in nlp_modules/patterns.py
        """

        pattern = re.compile(Regex.pattern_for_line)

        lines = pattern.findall(string=input_text)

        if not lines:
            return [input_text]

        reassembled_para = ''.join(lines)
        if reassembled_para != input_text:
            captured_substring_pattern = re.compile(reassembled_para)
            split_result: list = re.split(captured_substring_pattern, input_text)
            if len(split_result) > 1:
                pre_substring = split_result[0]
                post_substring = split_result[1]
                lines.insert(0, pre_substring)
                lines.append(post_substring)
            else:
                missed_substring = ''.join(split_result)
                if input_text.startswith(missed_substring):
                    lines.insert(0, missed_substring)
                elif input_text.endswith(missed_substring):
                    lines.append(missed_substring)
                else:
                    logger.error(
                        f'REGEX MATCH missed a substring in the middle of string. Input Text: {input_text} Result: {lines}')

        if ''.join(lines) != input_text:
            logger.error(f'REGEX MATCH did not include all characters. Input Text: {input_text} Result: {lines}')
            if AppConfig.STOP_RUN_IF_TEXT_PROCESSING_ERRORS:
                AppConfig.GLOBAL_RUN_STOP = True
                logger.warning(f'DEBUGGING MODE: GLOBAL RUN STOP FLAG SET')
            else:
                logger.warning(f'There was a text split error with {input_text}. Para will be considered to be a single line')
                lines = [input_text]

        lines = [line for line in lines if not FundamentalPatterns.contains_only_whitespace(line)]

        return lines

    @staticmethod
    def regex_split_to_clauses(input_text: str) -> list:
        """
        Splits the input text into clauses using a regular expression pattern for clause detection.

        Args:
            input_text (str): The input text to be split into clauses.

        Returns:
            list: A list of strings representing the clauses extracted from the input text.

        The function uses a regular expression pattern defined in `Regex.pattern_for_clause`
        to identify and extract clauses from the input text. If no clauses are found, the entire
        input text is returned as a single clause. The function also checks if the sum of extracted
        clauses matches the original input text and logs an error if discrepancies are found.

        If debugging mode (`AppConfig.PREVENT_TRANSMUTE_IF_TEXT_PROCESSING_ERRORS`) is enabled,
        the function may set the `GLOBAL_RUN_STOP` flag in `AppConfig` on error. Otherwise, it
        logs a warning and considers the entire input text as a single clause.

        Note:
        - Regex patterns are all defined in the Regex class in nlp_modules/patterns.py
        """

        pattern = re.compile(Regex.pattern_for_clause)

        clauses = pattern.findall(string=input_text)

        if not clauses:
            return [input_text]

        if ''.join(clauses) != input_text:
            logger.error(f'REGEX MATCH did not include all characters. Input Text: {input_text} Result: {clauses}')
            if AppConfig.STOP_RUN_IF_TEXT_PROCESSING_ERRORS:
                AppConfig.GLOBAL_RUN_STOP = True
                logger.warning(f'DEBUGGING MODE: GLOBAL RUN STOP FLAG SET')
            else:
                logger.warning(f'There was a text split error with {input_text}. Line will be considered to be a single clause')
                clauses = [input_text]

        clauses = [clause for clause in clauses if not FundamentalPatterns.contains_only_whitespace(clause)]

        return clauses

class Parser:

    @staticmethod
    def get_word_pos_from_jisho_html(jisho_html: str) -> list:

        # This function is intended to recieve the html zenbar section for a single sentence. But will handle multiple sentences.
        # Can be postprocessed to break at the . period separator in japanese

        soup = BeautifulSoup(jisho_html, 'html.parser')

        list_of_li_elements = soup.find_all('li', class_='japanese_word')

        regex_for_pos_tag = r'data-pos="([A-Za-z\s]+)"'
        regex_for_japanese_word = r'data-word="([A-Za-z0-9\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\u3000-\u303F\uFF65-\uFF9F]+)"'
        regex_for_Punctuation_symbols = r'([\u2000-\u206F\u3000-\u303F\uFF01-\uFF0F\uFF1A-\uFF20\uFF3B-\uFF40\uFF5B-\uFF65]+)'

        pos_tag_pattern = re.compile(regex_for_pos_tag, re.IGNORECASE)
        puctuation_pattern = re.compile(regex_for_Punctuation_symbols, re.IGNORECASE)
        data_word_pattern = re.compile(regex_for_japanese_word, re.IGNORECASE)

        list_of_pos_tags = list()
        list_of_words = list()

        for li_element in list_of_li_elements:
            # In this loop it is important to ensure that an elements are being added simultaneously to both lists, else the zip
            # Function at the end will fail.
            try:
                pos_tag_match = pos_tag_pattern.search(str(li_element))

                if pos_tag_match is None:
                    list_item_text_content = li_element.get_text
                    puctuation_match = puctuation_pattern.search(str(list_item_text_content))

                    if puctuation_match is not None:
                        pos_tag_match = 'Punctuation'
                        list_of_pos_tags.append(pos_tag_match)

                    else:
                        pos_tag_match = 'NONE'
                        list_of_pos_tags.append(pos_tag_match)
                else:
                    pos_tag_match = pos_tag_match.group(1)
                    list_of_pos_tags.append(pos_tag_match)

                # print(pos_tag_match)
            except Exception as e2:
                logger.error(f'{e2}')
                pos_tag_match = 'ERROR'
                list_of_pos_tags.append(pos_tag_match)
                pass

            try:

                word_match = data_word_pattern.search(str(li_element))

                if word_match is None:
                    list_item_text_content = li_element.get_text
                    puctuation_match = puctuation_pattern.search(str(list_item_text_content))

                    if puctuation_match is not None:
                        word_match = puctuation_match.group(1)
                        list_of_words.append(word_match)

                    else:
                        word_match = 'NONE'
                        list_of_words.append(word_match)

                else:
                    word_match = word_match.group(1)
                    list_of_words.append(word_match)

            except Exception as e2:
                logger.error(f'{e2}')
                word_match = 'ERROR'
                list_of_words.append(word_match)
                pass

        list_of_word_pos_tuples = [(word, pos_tag) for word, pos_tag in zip(list_of_words, list_of_pos_tags)]

        return list_of_word_pos_tuples


