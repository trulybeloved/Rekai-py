from typing import Set

from nlp_modules.kroatoanjp_fukuin.preprocess.sentence import Word, Sentence

class NamedEntityRecognizer:
    def is_name(self, value:str) -> bool:
        pass

    def get_name_words_from_sentence(self, sentence:Sentence) -> Set[Word]:
        name_word_set = set()
        for word in sentence.words:
            if self.is_name(word.text):
                name_word_set.add(word)
        return word