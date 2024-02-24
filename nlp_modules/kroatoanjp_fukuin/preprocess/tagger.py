from difflib import SequenceMatcher
import re
from typing import Optional, Iterable, List

from nlp_modules.kroatoanjp_fukuin.preprocess.tokenizer.tokenizer import Tokenizer
from nlp_modules.kroatoanjp_fukuin.preprocess.ner.basic_named_entity_recognizer import BasicNamedEntityRecognizer
from nlp_modules.kroatoanjp_fukuin.preprocess.sentence import Sentence, Word
from nlp_modules.kroatoanjp_fukuin.preprocess.tokenizer.part_of_speech import PartOfSpeech
from nlp_modules.kroatoanjp_fukuin.preprocess.utils import sort_list_by_string_length


class Tagger:

    # Arbitrary token used to replace punctuation which tokenizers 
    # handle poorly.
    PUNCTUATION_REPLACEMENT_TOKEN = "$$$"

    def __init__(
        self, 
        tokenizer:Tokenizer,
        # If True, will subdivide words that contain proper nouns, as
        # listed in proper_noun_list  
        tag_potential_proper_nouns:Optional[bool] = True, 
        proper_noun_list:Optional[Iterable[str]] = None
    ):
        self._name_recognizer = BasicNamedEntityRecognizer()
        self._tokenizer = tokenizer
        self._tag_potential_proper_nouns = tag_potential_proper_nouns
        self._proper_noun_list = []
        if proper_noun_list:
            # Sort list of additional taggable proper nouns from longest 
            # to shortest to avoid accidental replacements of a common
            # substring
            for word in sort_list_by_string_length(proper_noun_list, reverse=True):
                self._proper_noun_list.append(
                    Word(word, PartOfSpeech.PROPER_NOUN)
                )

    def tag(self, text:str) -> Sentence:
        NEWLINE_WORD = Word(text='\n', part_of_speech=PartOfSpeech.WHITESPACE)
        combined_word_list = []
        for line in text.split("\n"):
            tagged_sentence = self.tag_line(line)
            combined_word_list += tagged_sentence.words
            combined_word_list.append(NEWLINE_WORD)
        combined_word_list.pop() # Remove final added NEWLINE_WORD
        return Sentence(combined_word_list)

    def tag_line(self, text:str) -> Sentence:
        preprocessed_text = self._preprocess_text(text)
        word_list = self._tokenizer.tokenize(preprocessed_text)
        if self._tag_potential_proper_nouns:
            name_checked_word_list = []
            for word in word_list:
                if self._name_recognizer.is_name(word.text):
                    tagged_subwords = self._tag_with_word_list(
                        text=word.text, 
                        word_list=self._proper_noun_list, 
                        word_list_presorted=True
                    )
                    for subword in tagged_subwords:
                        name_checked_word_list.append(subword)
                else:
                    name_checked_word_list.append(word)
            word_list = name_checked_word_list
        tagged_sentence = Sentence(word_list)
        validated_tagged_sentence = self._validate_tagging(text, tagged_sentence)
        return validated_tagged_sentence


    # Divide a string into words with preference given to a list of
    # provided words. Any unrecognized words should then be retokenized.
    def _tag_with_word_list(
            self, 
            text:str, 
            word_list:List[Word],
            word_list_presorted=False
        ) -> List[Word]:
        if len(text) == 0:
            return []
        # Known words should be checked from longest to shortest to 
        # avoid unintentionally matching shorter words
        if word_list_presorted:
            sorted_word_list = word_list
        else:
            sorted_word_list = []
            len_tagged_word_list = {(len(word), word) for word in word_list}
            for word_len, word in sorted(len_tagged_word_list, reverse=True):
                sorted_word_list.append(word)
        tagged_words = [] 
        matching_word_found = False
        for i, word in enumerate(sorted_word_list):
            if word.text == text:
                tagged_words.append(word)
                matching_word_found = True
                break
            elif word.text in text:
                unchecked_words = sorted_word_list[i+1:]
                non_matching_text_parts = text.split(word.text)
                for part in non_matching_text_parts:
                    subword_list = self._tag_with_word_list(part, unchecked_words, True)
                    for subword in subword_list:
                        tagged_words.append(subword)
                    tagged_words.append(word)
                tagged_words.pop() # Last appended word is extra
                matching_word_found = True
                break
        # Default to tokenizer once all the words in the provided
        # word list have been tried
        if not matching_word_found:
            return self._tokenizer.tokenize(text)
        else:
            return tagged_words

    def _preprocess_text(self, text: str) -> str:
        # Tokenizers like Fugashi do not preserve whitespace, so replace 
        # with arbitrary punctuation token, and reintroduce the whitespace
        # after tagging.
        text = re.sub(r'\s',  Tagger.PUNCTUATION_REPLACEMENT_TOKEN, text)
        # Fugashi will treat words separated by '・' as one word, preventing
        # partial name replacements (ie. replacing last name only, if a full 
        # name replacement can't be made)
        text = text.replace('・', Tagger.PUNCTUATION_REPLACEMENT_TOKEN)
        return text

    def _validate_tagging(self, text: str, sentence: Sentence) -> Sentence:
        sentence_str = str(sentence)
        if text == sentence_str:
            return sentence
        seq_match = SequenceMatcher(None, text, sentence_str, autojunk=False)
        matching_blocks = seq_match.get_matching_blocks()
        old_word_list = list(sentence.words)
        old_word_list_starting_indices = []
        old_word_list_ending_indices = []
        current_starting_index = 0
        for word in old_word_list:
            old_word_list_starting_indices.append(current_starting_index)
            current_starting_index += len(word.text)
            old_word_list_ending_indices.append(current_starting_index - 1)
        # Validate that each matching block starts on the starting index of
        # one of the words, and ends on the ending index of one of the words
        # as opposed to in the middle a random word. Allows for mid-word 
        # discrepancies for punctuation-only words. Skip last block as it is
        # a dummy block with values (a=len(text), b=len(sentence), size=0).
        old_word_list_starting_index_set = set(old_word_list_starting_indices)
        old_word_list_ending_index_set = set(old_word_list_ending_indices)
        for block in matching_blocks[:-1]:
            block_starting_index = block.b
            block_ending_index = block.b + block.size - 1
            if block_starting_index not in old_word_list_starting_index_set:
                deviating_word_index = sentence.get_word_index_from_char_index(block_starting_index)
                deviating_word = old_word_list[deviating_word_index]
                if deviating_word.part_of_speech != PartOfSpeech.PUNCTUATION:
                    raise RuntimeError(
                        "Unexpected discrepancy between original text and tagged " + \
                        f"text occurred in the middle of a tagged word: {deviating_word}"
                    )
                # If a discrepancy is found in the middle of a punctuation word, split that word
                # into two words at the index where the discrepancy ends, and replace the old word
                # in the word and index lists
                deviating_word_starting_index = old_word_list_starting_indices[deviating_word_index]
                deviating_substr_len = block_starting_index - deviating_word_starting_index
                deviating_substr = deviating_word.text[:deviating_substr_len]
                matching_substr = deviating_word.text[deviating_substr_len:]
                deviating_sub_word = Word(deviating_substr, deviating_word.part_of_speech) 
                matching_sub_word = Word(matching_substr, deviating_word.part_of_speech)
                old_word_list.pop(deviating_word_index) 
                old_word_list.insert(deviating_word_index, deviating_sub_word) 
                old_word_list.insert(deviating_word_index + 1, matching_sub_word) 
                # Starting index of the deviating portion has not changed, so only the starting 
                # index of the matching portion needs to be added
                old_word_list_starting_indices.insert(deviating_word_index + 1, block_starting_index)
                # Ending index of the matching portion has not changed, so only the ending 
                # index of the deviating portion needs to be added
                old_word_list_ending_indices.insert(deviating_word_index, block_starting_index - 1)
                # Re-initialize sentence to account for changed indexes with the inserted words
                sentence = Sentence(old_word_list)
            if block_ending_index not in old_word_list_ending_index_set:
                deviating_word_index = sentence.get_word_index_from_char_index(block_ending_index)
                deviating_word = old_word_list[deviating_word_index]
                if deviating_word.part_of_speech != PartOfSpeech.PUNCTUATION:
                    raise RuntimeError(
                        "Unexpected discrepancy between original text and tagged " + \
                        f"text occurred in the middle of a tagged word: {deviating_word}"
                    )
                # If a discrepancy is found in the middle of a punctuation word, split that word
                # into two words at the index where the discrepancy starts, and replace the old word
                # in the word and index lists
                deviating_word_starting_index = old_word_list_starting_indices[deviating_word_index]
                matching_substr_len = block_ending_index - deviating_word_starting_index + 1
                matching_substr = deviating_word.text[:matching_substr_len]
                deviating_substr = deviating_word.text[matching_substr_len:]
                deviating_sub_word = Word(deviating_substr, deviating_word.part_of_speech) 
                matching_sub_word = Word(matching_substr, deviating_word.part_of_speech)
                old_word_list.pop(deviating_word_index) 
                old_word_list.insert(deviating_word_index, matching_sub_word) 
                old_word_list.insert(deviating_word_index + 1, deviating_sub_word) 
                # Starting index of the matching portion has not changed, so only the starting 
                # index of the deviating portion needs to be added
                old_word_list_starting_indices.insert(deviating_word_index + 1, block_ending_index + 1)
                # Ending index of the deviating portion has not changed, so only the ending 
                # index of the matching portion needs to be added
                old_word_list_ending_indices.insert(deviating_word_index, block_ending_index)
                # Re-initialize sentence to account for changed indexes with the inserted words
                sentence = Sentence(old_word_list)
                

        new_word_list = []
        current_block_index = 0
        current_word_index = 0
        # If there is only one matching block (the dummy block), there 
        # should be no common text between the original sentence and the
        # tagged sentence. This should only occur if the original 
        # sentence consisted only of punctuation that was replaced.
        # Validate that all tagged words are punctuation and then replace
        # with a single word containing all of the original text.
        if len(matching_blocks) == 1:
            while current_word_index < len(old_word_list):
                current_word = old_word_list[current_word_index]
                if current_word.part_of_speech != PartOfSpeech.PUNCTUATION:
                    raise RuntimeError(
                        f"Unexpected discrepancy in non-punctuation word: {current_word}"
                    )
                current_word_index += 1
            new_word_list.append(Word(text, current_word.part_of_speech))
        else:
            first_matching_block = matching_blocks[0]
            # If starting index of the first matching block between the 
            # original and tagged text starts at a non-zero index for
            # the original text, then the tagged text must be missing
            # some substring that was at the start of the original text
            if first_matching_block.a > 0:
                # Replace the non-matching initial set of words from the
                # tagged text with a single word containing the missing
                # string from the original text.
                missing_substring = text[:first_matching_block.a]
                first_matching_word_index = sentence.get_word_index_from_char_index(first_matching_block.b)
                while current_word_index < first_matching_word_index:
                    current_word = old_word_list[current_word_index]
                    if current_word.part_of_speech != PartOfSpeech.PUNCTUATION:
                        raise RuntimeError(
                            f"Unexpected discrepancy in non-punctuation word: {current_word}"
                        )
                    current_word_index += 1
                new_word_list.append(Word(missing_substring, current_word.part_of_speech))
                
        while current_block_index < len(matching_blocks) - 1 and \
            current_word_index < len(old_word_list):
            current_block = matching_blocks[current_block_index]
            # The range of indices such that any word whose starting index is
            # in this range will be matching between text and sentence_str
            current_matching_range_start = current_block.b
            current_matching_range_end = current_block.b + current_block.size
            current_matching_range = range(current_matching_range_start, current_matching_range_end)
            next_block = matching_blocks[current_block_index + 1]
            current_word = old_word_list[current_word_index]
            current_word_starting_index = old_word_list_starting_indices[current_word_index]
            current_word_ending_index = old_word_list_ending_indices[current_word_index]
            # If the entire word falls in the matching range, add the word to the
            # new sentence.
            if current_word_starting_index in current_matching_range and \
                current_word_ending_index in current_matching_range:
                new_word_list.append(current_word)
            else:
                if current_word.part_of_speech != PartOfSpeech.PUNCTUATION:
                    raise RuntimeError(
                        f"Unexpected discrepancy in non-punctuation word: {current_word}"
                    )
                if current_word_starting_index >= current_matching_range_end:
                    # If the current word lies beyond the current matching block,
                    # insert a word containing the expected substring from the 
                    # original text, and then update current block to the next 
                    # matching block.
                    if current_block.a + current_block.size < len(text):
                        # The substring of non-matching from the original text 
                        # will be between the indices:
                        # current_block.a + current_block.size = index of first 
                        #   non-matching character.
                        # next_block.a = index of first matching character of 
                        #   the next block.
                        expected_substring = text[current_block.a+current_block.size:next_block.a]
                        new_word_list.append(Word(expected_substring, current_word.part_of_speech))
                        current_block_index += 1
            current_word_index += 1
        validated_sentence = Sentence(new_word_list)
        if str(validated_sentence) != text:
            raise RuntimeError(
                "Failed to clean-up all discrepancies between original and tagged text.\n" + \
                f"Original: {text}\n"
                f"Tagged:   {validated_sentence}\n"
            )
        return validated_sentence