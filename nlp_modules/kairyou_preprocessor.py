"""
Credits
This module uses refactored code from an open source project.
Please find the source code of their open source project along with license information below.
We acknowledge and are grateful to Bikatr7 for their contributions to open source.

Project: Kudasai https://github.com/Bikatr7/Kudasai
License (GPL-3.0) https://raw.githubusercontent.com/Bikatr7/Kudasai/main/LICENSE.md

"""

## built-in libraries
import enum
import itertools
import typing
import string

## third-party libraries
import spacy
from loguru import logger

from appconfig import AppConfig
from custom_modules.custom_exceptions import KairyouException

class Name(typing.NamedTuple):
    """
    Represents a Japanese name along with its equivalent english name.
    The Name class extends the NamedTuple class, allowing for the creation of a tuple with named fields.
    """

    jap: str
    eng: str


## https://en.wikipedia.org/wiki/Katakana_(Unicode_block)
KATAKANA_CHARSET = {
    '゠', 'ァ', 'ア', 'ィ', 'イ', 'ゥ', 'ウ', 'ェ', 'エ', 'ォ', 'オ', 'カ', 'ガ', 'キ', 'ギ', 'ク',
    'グ', 'ケ', 'ゲ', 'コ', 'ゴ', 'サ', 'ザ', 'シ', 'ジ', 'ス', 'ズ', 'セ', 'ゼ', 'ソ', 'ゾ', 'タ',
    'ダ', 'チ', 'ヂ', 'ッ', 'ツ', 'ヅ', 'テ', 'デ', 'ト', 'ド', 'ナ', 'ニ', 'ヌ', 'ネ', 'ノ', 'ハ',
    'バ', 'パ', 'ヒ', 'ビ', 'ピ', 'フ', 'ブ', 'プ', 'ヘ', 'ベ', 'ペ', 'ホ', 'ボ', 'ポ', 'マ', 'ミ',
    'ム', 'メ', 'モ', 'ャ', 'ヤ', 'ュ', 'ユ', 'ョ', 'ヨ', 'ラ', 'リ', 'ル', 'レ', 'ロ', 'ヮ', 'ワ',
    'ヰ', 'ヱ', 'ヲ', 'ン', 'ヴ', 'ヵ', 'ヶ', 'ヷ', 'ヸ', 'ヹ', 'ヺ', '・', 'ー', 'ヽ', 'ヾ'
}

## Punctuation unicode ranges:
## https://kairozu.github.io/updates/cleaning-jp-text
PUNCTUATION_CHARSET = {
                          '　', '、', '。', '〃', '〄', '々', '〆', '〇', '〈', '〉', '《', '》', '「', '」', '『', '』',
                          '【', '】', '〒', '〓', '〔', '〕', '〖', '〗', '〘', '〙', '〚', '〛', '〜', '〝', '〞', '〟',
                          '〠', '〡', '〢', '〣', '〤', '〥', '〦', '〧', '〨', '〩', '〪', '〫', '〬', '〭', '〮', '〯',
                          '〰', '〱', '〲', '〳', '〴', '〵', '〶', '〷', '〸', '〹', '〺', '〻', '〼', '〽', '〾', '〿',
                          '！', '＂', '＃', '＄', '％', '＆', '＇', '（', '）', '＊', '＋', '，', '－', '．', '／', '：',
                          '；', '＜', '＝', '＞', '？', '［', '＼', '］', '＾', '＿', '｀', '｛', '｜', '｝', '～', '｟',
                          '｠', '｡', '｢', '｣', '､', '･', 'ー', '※', ' ', ' ', ' ', ' ', "«", "»",
                          ' ', ' ', ' ', ' ', ' ', ' ', ' ',
                          '​', '‌', '‍', '‎', '‏', '‐', '‑', '‒', '–', '—',
                          '―', '‖', '‗', '‘', '’', '‚', '‛', '“', '”', '„', '‟', '†', '‡', '•', '‣', '․', '‥', '…', '‧',
                          ' ', ' ', '‪', '‫', '‬', '‭', '‮',
                          ' ', '‰', '‱', '′', '″', '‴', '‵', '‶', '‷', '‸', '‹', '›', '※', '‼', '‽', '‾', '‿',
                          '⁀', '⁁', '⁂', '⁃', '⁄', '⁅', '⁆', '⁇', '⁈', '⁉', '⁊', '⁋', '⁌', '⁍', '⁎', '⁏', '⁐', '⁑', '⁒',
                          '⁓', '⁔', '⁕', '⁖', '⁗', '⁘', '⁙', '⁚', '⁛', '⁜', '⁝', '⁞', ' ', '⁠',
                          '⁦', '⁧', '⁨', '⁩', '«', '»', '×', "△", "▼"
                      } | set(string.punctuation)  ## EN punctuation set


##--------------------start-of-KatakanaHandler------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

class KatakanaHandler:
    """
    Contains helper functions for katakana handling.
    """

    katakana_words = []

    ##--------------------start-of-load_katakana_words()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def load_katakana_words() -> None:
        """
        Loads the katakana library into memory.
        """

        with open(AppConfig.path_to_katakana_words, "r", encoding="utf-8") as file:
            for line in file:
                KatakanaHandler.katakana_words.append(line.strip())

    ##--------------------start-of-is_katakana_only()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def is_katakana_only(string: str) -> bool:
        """
        Checks if the string_list is only katakana.

        Parameters:
        string_list (str) : the string_list to check.

        Returns:
        bool : True if the word is only katakana, False otherwise.
        """

        return all([char in KATAKANA_CHARSET for char in string])

    ##--------------------start-of-get_katakana_entities()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def get_katakana_entities(names: dict) -> typing.List[Name]:
        """
        Gets the katakana entities from the names dictionary.

        Returns:
        list (object - Name) : a list of Name objects.
        """

        return [Name(jap=j, eng=e) for e, j in names.items() if KatakanaHandler.is_katakana_only(j)]

    ##--------------------start-of-is_actual_word()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def is_actual_word(jap: str) -> bool:
        """
        Checks if the given japanese is an actual katakana word.

        Parameters:
        jap (str) : the katakana word to check.

        Returns:
        bool : True if the word is an actual katakana word, False otherwise.
        """

        if (jap in KatakanaHandler.katakana_words):
            return True
        else:
            return False

    ##--------------------start-of-is_punctuation()------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def is_punctuation(string: str):
        """
        Checks if the given string_list is all punctuation.

        Parameters:
        string_list (str) : the string_list to check.

        Returns:
        bool : True if the word is all punctuation, False otherwise.
        """

        return all([char in PUNCTUATION_CHARSET for char in string])


class ReplacementType(enum.Flag):
    """
    Represents how a name should be replaced when dealing with honorifics and overall replacements.

    The ReplacementType class extends the Flag class, allowing for the combination of name markers using bitwise operations.

    Name Markers:
    - NONE : No specific name marker.
    - FULL_NAME : Represents a full name, first and last name.
    - FIRST_NAME : Represents the first name only.
    - FULL_AND_FIRST : Represents both the full name and the first name separately.
    - LAST_NAME : Represents the last name only.
    - FULL_AND_LAST : Represents both the full name and the last name.
    - FIRST_AND_LAST : Represents both the first name and the last name.
    - ALL_NAMES : Represents all possible names.
    """

    NONE = 0
    FULL_NAME = 1
    FIRST_NAME = 2
    FULL_AND_FIRST = 3
    LAST_NAME = 4
    FULL_AND_LAST = 5
    FIRST_AND_LAST = 6
    ALL_NAMES = 7


class Kairyou:
    """
    self is the preprocessor for the Kudasai program.
    """

    ## The dictionary containing the rules for preprocessing.
    replacements_json: dict
    text_to_preprocess: str
    total_replacements = 0

    replacement_json_sections = ["kutouten",
                                 "unicode",
                                 "phrases",
                                 "single_words",
                                 "enhanced_check_whitelist",
                                 "full_names",
                                 "single_names",
                                 "name_like",
                                 "honorifics"]

    ## How japanese names are separated in the japanese text
    JAPANESE_NAME_SEPARATORS = ["・", ""]

    ## The spacy NER model used for enhanced replacement checking.
    ner = spacy.load("ja_core_news_lg")

    ## (title, json_key, is_name, replace_name, honorific_type)
    replacement_rules = [
        ('Punctuation', 'kutouten', False, None, None),
        ('Unicode', 'unicode', False, None, None),
        ('Phrases', 'phrases', False, None, None),
        ('Words', 'single_words', False, None, None),
        ('Enhanced Check Whitelist', 'enhanced_check_whitelist', True, ReplacementType.ALL_NAMES,
         ReplacementType.ALL_NAMES),
        ('Full Names', 'full_names', True, ReplacementType.ALL_NAMES, ReplacementType.ALL_NAMES),
        ('Single Names', 'single_names', True, ReplacementType.ALL_NAMES, ReplacementType.ALL_NAMES),
        ('Name Like', 'name_like', True, ReplacementType.ALL_NAMES, ReplacementType.NONE),
    ]

    def __init__(self, text_to_preprocess, replacements_json):

        self.text_to_preprocess = text_to_preprocess
        self.replacements_json = replacements_json
        self.validate_replacement_json()


    def validate_replacement_json(self) -> None:

        try:
            for section in self.replacement_json_sections:
                assert section in self.replacements_json

        except AssertionError as e:
            logger.error(
                "Invalid replacement json file. Missing keys. Please check the jsons folder for an example replacement json file.")
            raise e

    def preprocess(self) -> None:

        logger.info('Preprocessing...')
        self.total_replacements = 0

        replacement_rules = self.replacement_rules

        replaced_names = dict()

        self.replace_non_katakana(replacement_rules, replaced_names)
        self.replace_katakana(replacement_rules, replaced_names)


    def replace_non_katakana(self, replacement_rules: list, replaced_names: dict) -> None:
        """

        Handles non-katakana replacements.

        Parameters:
        replacement_rules (list) : The rules to replace by.
        replaced_names (dict - str) : Names we have replaced.

        """

        ## for non-katakana replacements
        for rule in replacement_rules:

            title, json_key, is_name, replace_name_param, honorific_type = rule

            if (is_name == True):

                try:
                    for eng, jap in self.replacements_json[json_key].items():

                        ## makes jap entries into a list if not already
                        if (isinstance(jap, list) == False):
                            jap = [jap]

                        current_name = Name(" ".join(jap), eng)

                        ## katakana is replaced at the end
                        if (KatakanaHandler.is_katakana_only(current_name.jap)):
                            continue

                        self.replace_name(current_name, replace_name_param, honorific_type, replaced_names, json_key,
                                          is_potential_name=True, is_katakana=False)

                except Exception as E:
                    raise KairyouException
                finally:
                    continue

            else:
                try:
                    for jap, eng in self.replacements_json[json_key].items():
                        self.replace_single_word(jap, eng, is_potential_name=False)

                except Exception as E:
                    logger.exception(E)
                    raise KairyouException
                finally:
                    continue

    def replace_katakana(self, replacement_rules: list, replaced_names: dict) -> None:
        """

        Handles katakana replacements.

        Parameters:
        replacement_rules (list) : The rules to replace by.
        replaced_names (dict - str) : Names we have replaced.

        """

        katakana_entries = []

        for rule in replacement_rules:

            title, json_key, is_name, replace_name_param, honorific_type = rule

            if (is_name == True):

                for eng, jap in self.replacements_json[json_key].items():

                    ## makes jap entries into a list if not already
                    if (isinstance(jap, list) == False):
                        jap = [jap]

                    current_name = Name(" ".join(jap), eng)

                    if (KatakanaHandler.is_katakana_only(current_name.jap) and not KatakanaHandler.is_actual_word(
                            current_name.jap)):
                        katakana_entries.append((current_name, replace_name_param, honorific_type, json_key))
            else:

                for jap, eng in self.replacements_json[json_key].items():

                    if (KatakanaHandler.is_katakana_only(jap) and not KatakanaHandler.is_actual_word(jap)):
                        katakana_entries.append((jap, eng))

        ## Sort the katakana entries by the length of Japanese phrases in descending order
        katakana_entries.sort(key=lambda entry: len(entry[0].jap if isinstance(entry[0], Name) else entry[0]), reverse=True)

        ## Replace katakana names and words
        for entry in katakana_entries:

            ## names
            if (isinstance(entry[0], Name)):

                current_name, replace_name_param, honorific_type, json_key = entry

                try:
                    self.replace_name(current_name, replace_name_param, honorific_type, replaced_names, json_key,
                                      is_potential_name=True, is_katakana=True)

                except Exception as E:
                    logger.exception(E)
                    raise KairyouException
                finally:
                    continue

            else:

                ## Handling non-names
                jap, eng = entry

                try:
                    self.replace_single_word(jap, eng, is_potential_name=False, is_katakana=True)

                except Exception as E:
                    logger.exception(E)
                    raise KairyouException
                finally:
                    continue

    def yield_name_replacements(self, Name: Name, replace_type: ReplacementType, honorific_type: ReplacementType) -> \
            typing.Generator[tuple[str, str, bool], None, None]:
        """

        Generates tuples of English and Japanese names to be replaced, along with a boolean indicating whether honorifics should be kept or removed.

        Parameters:
        Name (object - Name) : represents a japanese name along with its english equivalent.
        replace_type  (object - ReplacementType) : how a name should be replaced.
        honorific_type (object - ReplacementType) : how a honorific_type should be replaced.

        Returns:
        tuple (string_list, string_list, bool) : tuple containing the japanese name, english name, and a boolean indicating whether honorifics should be kept or removed.

        tuple is wrapped in a generator along with two None values. No, I don't know why.

        """

        japanese_names = Name.jap.split(" ")
        english_names = Name.eng.split(" ")

        ## if the lengths of the names don't match, the entire Name is invalid
        try:

            assert len(japanese_names) == len(english_names)

        except AssertionError as e:
            logger.error(f"Name lengths do not match for : {Name}. Please correct Name discrepancy in JSON")
            raise e

        if (ReplacementType.FULL_NAME in replace_type):
            indices = range(len(japanese_names))

            ## create a chain of combinations of indices, starting with combinations of length 1 up to the length of indices
            combinations = itertools.chain(*(itertools.combinations(indices, i) for i in range(2, len(indices) + 1)))
            for comb in combinations:
                for separator in self.JAPANESE_NAME_SEPARATORS:
                    yield (" ".join(map(lambda i: english_names[i], comb)),
                           separator.join(map(lambda i: japanese_names[i], comb)),
                           ReplacementType.FULL_NAME in honorific_type)

        if (ReplacementType.FIRST_NAME in replace_type):
            yield (english_names[0],
                   f'{japanese_names[0]}',
                   ReplacementType.FIRST_NAME in honorific_type)

        if (ReplacementType.LAST_NAME in replace_type):
            yield (english_names[-1],
                   f'{japanese_names[-1]}',
                   ReplacementType.LAST_NAME in honorific_type)


    def replace_single_word(self, word: str, replacement: str, is_potential_name: bool, is_katakana: bool = False) -> int:
        """

        Replaces a single word in the Japanese text, with an additional check for Katakana words.

        The function is extremely picky with katakana in general.

        Parameters:
        word (string_list) : The word to be replaced.
        replacement (string_list) : The replacement for the word.
        is_katakana (bool | optional | default=false) : Indicates if the word is in Katakana.

        Returns:
        num_occurrences (int) : The number of occurrences of the word replaced.

        """

        num_occurrences = 0

        if (is_katakana):

            ## Skip replacement if it's an actual word.
            if (KatakanaHandler.is_actual_word(word)):
                return 0

            else:

                ## Use NER to ensure we're not replacing a proper name that's not in our list of Katakana words.
                if (is_potential_name):
                    self.perform_enhanced_replace(word, replacement)

                else:
                    num_occurrences = self.text_to_preprocess.count(word)
                    if (num_occurrences > 0):
                        self.text_to_preprocess = self.text_to_preprocess.replace(word, replacement)

        else:
            num_occurrences = self.text_to_preprocess.count(word)
            if (num_occurrences > 0):
                self.text_to_preprocess = self.text_to_preprocess.replace(word, replacement)

        self.total_replacements += num_occurrences

        return num_occurrences


    def replace_name(self, Name: Name, replace_type: ReplacementType, honorific_type: ReplacementType, replaced_names: dict,
                     json_key: str, is_potential_name: bool, is_katakana: bool) -> None:
        """

        Replaces names in the japanese text based off of tuples returned by yield_name_replacements.

        Parameters:
        Name (object - Name)  : represents a japanese name along with its english equivalent.
        replace_type  (object - ReplacementType) : how a name should be replaced.
        honorific_type (object - ReplacementType) : how a honorific should be replaced.
        replaced_names (dict - string_list) : a dict of replaced names and their occurrences.
        is_katakana (bool) : Indicates if the name is in Katakana.

        """

        for eng, jap, no_honor in self.yield_name_replacements(Name, replace_type, honorific_type):

            ## Skip the replacement if this name has already been processed.
            if (jap in replaced_names):
                continue

            replacement_data = dict()

            ## Process honorifics if necessary
            for honor, honorific_english in self.replacements_json['honorifics'].items():
                replacement_data[honorific_english] = self.replace_single_word(
                    f'{jap}{honor}',
                    f'{eng}-{honorific_english}',

                    ## if honorifics, don't worry about additonal checking
                    is_potential_name=False,
                    is_katakana=False,
                )

            if (is_katakana):
                ## Skip replacement if it's an actual Katakana word.
                if (KatakanaHandler.is_actual_word(jap)):
                    continue
                else:
                    ## Perform enhanced replacement check with NER
                    self.perform_enhanced_replace(jap, eng)

            ## If the name does not have honorific and isn't a known Katakana word, or we aren't checking for Katakana
            if no_honor:
                if json_key == "enhanced_check_whitelist" or len(jap) == 1:
                    self.perform_enhanced_replace(jap, eng)

                else:
                     self.replace_single_word(jap, eng, is_potential_name, is_katakana)


    def perform_enhanced_replace(self, jap: str, replacement: str) -> None:
        """

        Uses ner (Named Entity Recognition) from the spacy module to replace names that need to be more carefully replaced, such as single kanji, katakana names, or those placed in the user whitelist.

        May miss true positives, but should not replace false positives.

        Parameters:
        jap (str) : Japanese to be replaced.
        replacement (str) : the replacement for the Japanese

        Returns:
        jap_replace_count (int) : How many japanese replacements that were made.

        """

        i = 0
        jap_replace_count = 0

        jap_lines = self.text_to_preprocess.split('\n')

        while (i < len(jap_lines)):
            if (jap in jap_lines[i]):

                sentence = self.ner(jap_lines[i])

                for entity in sentence.ents:
                    if (entity.text == jap and entity.label_ == "PERSON"):
                        jap_replace_count += 1
                        jap_lines[i] = jap_lines[i][:entity.start_char] + replacement + jap_lines[i][entity.end_char:]

            i += 1

        self.text_to_preprocess = '\n'.join(jap_lines)
        self.total_replacements += jap_replace_count

        return

