from bisect import bisect_right
from typing import Iterable, NamedTuple

class Word(NamedTuple):
    text:str
    part_of_speech:str

class Sentence:
    def __init__(self, words:Iterable[Word]):
        self.words = tuple(words)
        # Calculate word starting indexes in advance
        starting_indexes = []
        current_starting_index = 0
        for word in words:
            starting_indexes.append(current_starting_index)
            current_starting_index += len(word.text)
        self._word_starting_indexes = tuple(starting_indexes)
        self._str = "".join([word.text for word in self.words])

    def __eq__(self, other) -> bool:
        if not isinstance(other, Sentence):
            return False
        return self.words == other.words


    # Replaces the text in a single tagged word with a new string
    def replace_word(self, old_word:Word, new_text:str) -> "Sentence":
        word_list = []
        for word in self.words:
            if word == old_word:
                word_list.append(old_word._replace(text=new_text))
            else:
                word_list.append(word)
        return Sentence(word_list)    

    # If 1+ sequential whole words match a given string, it will replace 
    # the entire matching sequence with a single word containing the 
    # replacement string
    def replace_multi_word_sequence(self, old_text:str, new_word:Word) -> "Sentence":
        sentence_str = str(self)
        if old_text not in sentence_str:
            return Sentence(self.words)
        search_starting_index = 0
        all_matches_found = False
        word_list = []
        while not all_matches_found:
            search_starting_word_index = self.get_word_index_from_char_index(search_starting_index)
            # Perform plain text search to quickly determine if there
            # are any remaining matches. If no matches are found, add the 
            # remaining words to the word list
            current_match_index = sentence_str.find(old_text, search_starting_index)
            if current_match_index == -1:
                word_list += self.words[search_starting_word_index:]
                all_matches_found = True
            else:
                matching_word_index = self.get_word_index_from_char_index(current_match_index)
                matching_word = self.words[matching_word_index]
                # Since the first potential replacement occurs at matching_word_index, all words
                # between the search_starting_word_index and matching_word_index can be added to
                # the word list
                word_list += self.words[search_starting_word_index:matching_word_index]
                sequence_word_count = 0
                current_sequence = ""
                match_found = False
                # Logic is essentially duplicated from Sentence.count
                while len(current_sequence) < len(old_text) and \
                    matching_word_index + sequence_word_count < len(self.words):
                    current_sequence_word = self.words[matching_word_index + sequence_word_count]
                    current_sequence += current_sequence_word.text
                    if not old_text.startswith(current_sequence):
                        break
                    elif current_sequence == old_text:
                        word_list.append(new_word)
                        match_found = True
                        search_starting_index = current_match_index + len(old_text)
                    sequence_word_count += 1
                if not match_found:
                    word_list.append(matching_word)
                    if matching_word_index + 1 < len(self.words):
                        search_starting_index = self._word_starting_indexes[matching_word_index + 1]
                    else:
                        all_matches_found = True 
            if search_starting_index >= len(sentence_str):
                all_matches_found = True   
        new_sentence = Sentence(word_list)      
        return new_sentence

    # Return the number of occurences of a given string, where each occurence
    # indicates that the string has appeared in the sentence as a sequence of 
    # whole words
    def count(self, query:str) -> int:
        sentence_str = str(self)
        match_count = 0
        search_starting_index = 0
        all_matches_found = False
        while not all_matches_found:
            # Perform plain text search to quickly determine if there
            # are any remaining matches.
            current_match_index = sentence_str.find(query, search_starting_index)
            if current_match_index == -1:
                all_matches_found = True
            else:
                matching_word_index = self.get_word_index_from_char_index(current_match_index)
                matching_word = self.words[matching_word_index]
                sequence_word_count = 0
                current_sequence = ""
                match_found = False
                # If one of the words in the sentence matches the beginning of
                # the string to be replaced, create a sequence starting with that
                # word and adding the following words until the sequence either
                # matches the query, reaches the end of the sentence without fully matching, 
                # or encounters a word that does not match the string to be replaced. 
                # If a match is found resume the parent loop after incrementing the search starting 
                # index to after the last index of the previous match. Otherwise increment the
                # search starting index to the starting index of the next word
                while len(current_sequence) < len(query) and \
                    matching_word_index + sequence_word_count < len(self.words):
                    current_sequence_word = self.words[matching_word_index + sequence_word_count]
                    current_sequence += current_sequence_word.text
                    if not query.startswith(current_sequence):
                        break
                    elif current_sequence == query:
                        match_found = True
                    sequence_word_count += 1
                if match_found:
                    match_count += 1
                    search_starting_index = current_match_index + len(query)
                elif matching_word_index + 1 < len(self.words):
                    search_starting_index = self._word_starting_indexes[matching_word_index + 1]
                else:
                    all_matches_found = True 
        return match_count

    # Return the number of occurences of a given word, 
    def count_word(self, query_word:Word) -> int:
        match_count = 0
        for word in self.words:
            if word == query_word:
                match_count += 1
        return match_count

    def get_word_index_from_char_index(self, char_index:int) -> int:
        if char_index < 0:
            raise IndexError(
                f"Index must be greater than or equal to 0. Received negative index: {char_index}"
            )
        elif char_index >= len(str(self)):
            raise IndexError(f"Index out of bounds: {char_index}")
        word_index = bisect_right(self._word_starting_indexes, char_index) - 1
        return word_index

    def __repr__(self):
        return self._str