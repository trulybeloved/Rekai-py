from typing import Optional, List

import fugashi

from nlp_modules.kroatoanjp_fukuin.preprocess.tokenizer.tokenizer import Tokenizer
from nlp_modules.kroatoanjp_fukuin.preprocess.sentence import Word
from nlp_modules.kroatoanjp_fukuin.preprocess.tokenizer.part_of_speech import PartOfSpeech

class FugashiTokenizer(Tokenizer):
    def __init__(
        self, 
        user_dic_path:Optional[str] = None # Path to MeCab user dic
    ):
        if user_dic_path:
            self._tagger = fugashi.Tagger(f"-u {user_dic_path}")
        else:
            self._tagger = fugashi.Tagger()

    def tokenize(self, text:str) -> List[Word]:
        word_list = []
        tagged_words = self._tagger(text)
        for word in tagged_words:
            word_text = word.surface
            # TODO: Add an explanation of the word.feature tuple
            part_of_speech = word.feature[0]
            # Prefer the more specific proper noun pos tag when available,
            # as it enables more accurate single kanji replacement
            if word.feature[0] == PartOfSpeech.NOUN and \
                word.feature[1] == PartOfSpeech.PROPER_NOUN:
                part_of_speech = word.feature[1]
            word_list.append(Word(word_text, part_of_speech))
        return word_list