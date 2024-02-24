from typing import Optional, List

import spacy
import sudachipy.tokenizer
from sudachipy import dictionary

from nlp_modules.kroatoanjp_fukuin.preprocess.tokenizer.sudachi_tokenizer import SudachiTokenizer
from nlp_modules.kroatoanjp_fukuin.preprocess.sentence import Word
from nlp_modules.kroatoanjp_fukuin.preprocess.tokenizer.part_of_speech import PartOfSpeech
from nlp_modules.kroatoanjp_fukuin.preprocess.utils import is_punctuation

# spaCy (https://spacy.io/) uses Sudachi for tokenization for its JP
# NLP processing pipelines. As a result, we can use user dictionaries
# with spaCy by replacing their underlying Sudachi tokenizer instance
# with one we instantiate ourselves.
class SpacyTokenizer(SudachiTokenizer):
    def __init__(
        self, 
        user_dic_path:Optional[str] = None # Path to Sudachi user dic
    ):
        self._tagger = spacy.load("ja_core_news_lg")
        if user_dic_path:
            # It is unlikely that spaCy will stop using Sudachi for
            # tokenization in the near future. Any changes to the 
            # underlying tokenization, if they occur, should be handled
            # here.
            if isinstance(self._tagger.tokenizer.tokenizer, sudachipy.tokenizer.Tokenizer):   
                self._user_dic_path = user_dic_path
                # Sudachi reads the user dictionaries that are listed in its
                # config, but requires the config be passed as a path to
                # a json file rather than being passed directly
                config_path = self._generate_temporary_sudachi_config_file()
                tokenizer = dictionary.Dictionary(config_path=config_path).create()
                self._delete_temporary_sudachi_config_file(config_path)
                self._tagger.tokenizer.tokenizer = tokenizer
            else:
                raise Exception("Unable to replace spaCy tokenizer.")


    def tokenize(self, text:str) -> List[Word]:
        word_list = []
        tagged_words = self._tagger(text)
        for word in tagged_words:
            word_text = word.text
            # Each spaCy tagged words has two attributes that indicate
            # part of speech. word.tag_ seems to return what the 
            # underlying tokenizer outputted (in this case Sudachi), 
            # while the word.pos_ returns what spaCy's model indicated
            # for the part of speech. However, in order to make use of
            # spaCy's tagging, we need to first map it back to the
            # Unidic POS format
            if word.pos_ not in SPACY_UNIDIC_POS_MAP:
                print(word.pos_)
                print(word.tag_)
                print(word.text)
            part_of_speech_tuple = SPACY_UNIDIC_POS_MAP[word.pos_]
            part_of_speech = part_of_speech_tuple[0]
            # Some tokenizers (Sudachi, Nagisa) tend to mistag long
            # strings of punctuation
            if part_of_speech != PartOfSpeech.PUNCTUATION and \
               is_punctuation(word_text):
               part_of_speech = PartOfSpeech.PUNCTUATION
            # Prefer the more specific proper noun pos tag when available,
            # as it enables more accurate single kanji replacement
            elif part_of_speech_tuple[0] == PartOfSpeech.NOUN and \
                 part_of_speech_tuple[1] == PartOfSpeech.PROPER_NOUN:
                part_of_speech = part_of_speech_tuple[1]
            word_list.append(Word(word_text, part_of_speech))
        return word_list

# https://github.com/explosion/spaCy/blob/b69d249a223fa4e633e11babc0830f3b68df57e2/spacy/lang/ja/tag_map.py
# https://github.com/explosion/spaCy/blob/b69d249a223fa4e633e11babc0830f3b68df57e2/spacy/lang/ja/tag_orth_map.py
# Maps each spaCy pos tag to its most generic Unidic equivalent
# TODO: Add an explanation of the unidic part of speech tuple
SPACY_UNIDIC_POS_MAP = {
    "PUNCT": ("補助記号","*","*","*"),
    "INTJ": ("感動詞","*","*","*"),
    "ADJ": ("形容詞","*","*","*"),
    "AUX": ("助動詞","*","*","*"),
    "ADP": ("助詞","*","*","*"),
    "PART": ("接尾辞","*","*","*"),
    "SCONJ": ("助詞","*","*","*"),
    "NOUN": ("名詞","普通名詞","*","*"),
    "SYM": ("補助記号","*","*","*"),
    "PRON": ("代名詞","*","*","*"),
    "VERB": ("動詞","一般","*","*"),
    "ADV": ("副詞","*","*","*"),
    "PROPN": ("名詞","固有名詞","*","*"),
    "NUM": ("名詞","数詞","*","*"),
    "DET": ("連体詞","*","*","*"),
    "SPACE": ("空白","*","*","*"),
    "CCONJ": ("接続詞","*","*","*"),
    "X": ("補助記号","*","*","*"),
}
