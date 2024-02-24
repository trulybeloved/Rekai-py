from enum import Enum

# Subset of the Unidic part of speech tags, as listed:
# https://gist.github.com/masayu-a/e3eee0637c07d4019ec9
class PartOfSpeech(str, Enum): 
    NOUN = "名詞"
    PROPER_NOUN = "固有名詞"
    PUNCTUATION = "補助記号"
    WHITESPACE = "空白"