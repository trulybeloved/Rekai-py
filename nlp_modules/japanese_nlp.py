"""Functions related to japanese NLP"""

import re

from bs4 import BeautifulSoup
from loguru import logger
import pykakasi
import MeCab
from sudachipy import Dictionary

from Rekai.nlp_modules.basic_nlp import FundamentalPatterns
from Rekai.nlp_modules.patterns import Regex, Charsets


class Classifier:

    @staticmethod
    def contains_no_parsable_ja_text(input_text: str) -> bool:

        print(input_text)
        replacement_set = Charsets.EXPRESSIONS | Charsets.PUNCTUATION
        for char in replacement_set:
            input_text = input_text.replace(char, '')

        # further checks on the remaining string
        same_kana_repeated = bool(re.match(Regex.same_hiragana_repeated, input_text))
        if same_kana_repeated:
            input_text = ''
        # Needs an additional dictionary based check
        return bool(len(input_text) < 1)

    @staticmethod
    def contains_no_kanji(input_text: str) -> bool:
        regex_pattern_for_any_kanji = re.compile(Regex.any_single_kanji, re.IGNORECASE)
        is_kanji_present: bool = bool(regex_pattern_for_any_kanji.search(input_text))
        if is_kanji_present:
            return False
        else:
            return True

print(Classifier.contains_no_parsable_ja_text('「「お客様――？」」'))
print(Classifier.contains_no_parsable_ja_text('※※　※　※　※　※　※　※　※　※　※　※　※'))
print(Classifier.contains_no_parsable_ja_text('　　　　　　　　　　　　　　　　△▼△▼△▼△'))
print(Classifier.contains_no_parsable_ja_text('「たたたたたたたたたたたたたた――っ！！」'))
print(Classifier.contains_no_parsable_ja_text('「――――」'))

class Extractor:
    @staticmethod
    def extract_kanji_block(input_text: str) -> tuple[str, str]:
        regex_pattern_for_kanji_block = re.compile(Regex.continuous_blocks_of_kanji)
        kanji_block_match = regex_pattern_for_kanji_block.match(input_text)
        kanji_block = kanji_block_match.group(0)
        non_kanji_block = input_text.replace(kanji_block, '')
        return kanji_block, non_kanji_block

#
# print(Classifier.contains_no_kanji('濃'))
# print(Classifier.contains_no_kanji('だ'))
# print(Extractor.extract_kanji_block('解な'))

class TextSplitter:

    @staticmethod
    def split_para_to_list_of_lines(input_text: str, *, strip_each_line: bool = True, trim_list: bool = True,
                                    delimiter: str = '。') -> list:

        if delimiter in input_text:
            list_of_lines = input_text.split(delimiter)
        else:
            list_of_lines = [input_text]
            return list_of_lines

        if strip_each_line:
            list_of_lines = [line.strip() for line in list_of_lines]

        if trim_list:
            list_of_lines = [line for line in list_of_lines
                             if not FundamentalPatterns.contains_only_whitespace(line)]

        list_of_lines = [f'{line}{delimiter}' for line in list_of_lines]

        return list_of_lines

    @staticmethod
    def split_line_to_list_of_clauses(input_text: str, *, strip_each_line: bool = True, trim_list: bool = True,
                                      delimiter: str = '、') -> list:

        if delimiter in input_text:
            list_of_clauses = input_text.split(delimiter)
        else:
            list_of_clauses = [input_text]
            return list_of_clauses

        if strip_each_line:
            list_of_clauses = [clause.strip() for clause in list_of_clauses]

        if trim_list:
            list_of_clauses = [clause for clause in list_of_clauses
                               if not FundamentalPatterns.contains_only_whitespace(clause)]

        if len(list_of_clauses) > 1:  # This statement would be redundant given the check above, consider removal
            final_list = [f'{clause}{delimiter}' for clause in list_of_clauses[:-1]]
            final_list.append(list_of_clauses[-1])
        else:
            final_list = list_of_clauses

        return final_list


class Parser:
    @staticmethod
    def parse_html(html_code):
        # Parse the HTML code
        soup = BeautifulSoup(html_code, 'html.parser')

        # Find all <li> elements with class "japanese_word"
        japanese_word_elements = soup.find_all('li', class_='japanese_word')

        # Extract and return the values of data-pos
        data_pos_values = [element['data-pos'] for element in japanese_word_elements]
        return data_pos_values

    @staticmethod
    def jisho_parse_html_parser(jisho_html: str) -> list:

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

        # print(list_of_pos_tags)
        # print(len(list_of_pos_tags))
        # print(list_of_words)
        #
        # print(len(list_of_words))
        # print(list_of_word_pos_tuples)
        # print(len(list_of_word_pos_tuples))

        return list_of_word_pos_tuples

    @staticmethod
    def add_type_to_words(japanese_text):
        pos_mapping = {
            '名詞': 'Noun',
            '動詞': 'Verb',
            '形容詞': 'Adjective',
            '副詞': 'Adverb',
            '助詞': 'Particle',
            '助動詞': 'Auxiliary verb',
            '記号': 'Symbol',
            'フィラー': 'Filler',
            '接続詞': 'Conjunction',
            '接頭詞': 'Prefix',
            '感動詞': 'Interjection',
            '未知語': 'Unknown',
            'その他': 'Other'
        }
        # Create an instance of the MeCab Tagger
        tagger = MeCab.Tagger('-r /dictionaries -d /dictionaries/mydic')

        # Parse the Japanese text
        parsed_text = tagger.parse(japanese_text)

        # Split the parsed text into individual lines
        lines = parsed_text.split('\n')

        # Process each line to extract the word and convert it to Romaji
        processed_lines = []
        for line in lines:
            if line == 'EOS':
                break
            else:
                # Split the line by tabs to extract the word and its features
                parts = line.split('\t')

                # Extract the word from the parts
                word = parts[0]

                # Extract the features from the parts
                features = parts[1].split(',')

                # Extract the most common meaning (part-of-speech) from the features
                pos = features[0]

                # Map the Japanese part-of-speech to its English equivalent
                english_pos = pos_mapping.get(pos)

                # Add the English part-of-speech in brackets after the word
                word_with_meaning = f"{word} ({english_pos})"

                # Append the processed line to the list
                processed_lines.append(word_with_meaning)

        # Join the processed lines to form the final text
        final_text = ' '.join(processed_lines)

        return final_text

    @staticmethod
    def tag_pos(text):
        mecab = MeCab.Tagger("-Ochasen")
        node = mecab.parse(text).split('\n')
        result = []

        for i in node[:-2]:
            col = i.split('\t')
            word = col[0]
            pos = col[3].split('-')[0]
            result.append(f'{word}({pos})')

        return ' '.join(result)

    @staticmethod
    def tag_pos_sudachi(text):
        dict_obj = Dictionary(dict_type='full')
        tokenizer_obj = dict_obj.create()

        # Manual mapping from Japanese POS tags to English equivalents
        pos_map = {
            "名詞": "Noun",
            "動詞": "Verb",
            "形容詞": "Adjective",
            "副詞": "Adverb",
            "接続詞": "Conjunction",
            "助詞": "Particle",
            "助動詞": "Auxiliary verb",
            "感動詞": "Interjection",
            "記号": "Symbol",
            "連体詞": "Adnominal",
            "代名詞": "Pronoun",
            "フィラー": "Filler",
            "未知語": "Unknown",
            "補助記号": "Symbol",
            "形状詞": "Na-adjective"
        }

        result = []

        tokens = tokenizer_obj.tokenize(text)
        # print(tokens.get_internal_cost())
        # print(tokens.__repr__())
        # token = tokens[0]
        # print(token.__repr__())
        # print(f'SURFACE: {token.surface()}')
        # print(f'RAW SURFACE: {token.raw_surface()}')
        # print(f'DICTIONARY_FORM: {token.dictionary_form()}')
        # print(f'DICTIONARY ID: {token.dictionary_id()}')
        # print(f'NORMALIZED FORM: {token.normalized_form()}')

        for token in tokenizer_obj.tokenize(text):
            word = token.surface()
            pos_japanese = token.part_of_speech()[0]

            # Map the Japanese POS tag to an English equivalent if possible
            pos_english = pos_map.get(pos_japanese, pos_japanese)
            result.append((word, pos_english))
        print(''.join(f'{word}:{pos_english}' for (word, pos_english) in result))

        return result

    @staticmethod
    def get_furigana(input_text):
        transmuter = pykakasi.Kakasi()
        transmuted_results = transmuter.convert(input_text)
        print(transmuted_results)
        for item in transmuted_results:
            return f'{item["hira"]}'

    @staticmethod
    def get_hepburn(input_text):
        transmuter = pykakasi.Kakasi()
        transmuted_results = transmuter.convert(input_text)
        print(transmuted_results)
        hepburn = ''
        for item in transmuted_results:
            hepburn += f'{item["hepburn"]} '
        hepburn = hepburn.strip()
        return hepburn

# print(Parser.get_hepburn('違いすぎていた'))

# print(TextSplitter.split_para_to_list_of_lines(test_text))

# print(f'SUDACHI: {Parser.tag_pos_sudachi(test_tokeizer)}')
# print(f'MeCAB: {Parser.add_type_to_words(test_tokeizer)}')
