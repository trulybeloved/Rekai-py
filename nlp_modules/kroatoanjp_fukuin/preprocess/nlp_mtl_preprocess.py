#!/usr/bin/env python

import time

from enum import Flag
from typing import NamedTuple, Optional, List
import itertools

from nlp_modules.kroatoanjp_fukuin.preprocess.tagger import Tagger
from nlp_modules.kroatoanjp_fukuin.preprocess.tokenizer.part_of_speech import PartOfSpeech
from nlp_modules.kroatoanjp_fukuin.preprocess.sentence import Word

# Bitwise flags for parts of names. The __contains__ operation for 
# members is defined such that A.__contains__(B) is True if A has
# atleast all of B's flags set.
#
# FULL_NAME = 1         #0001
# FIRST_NAME = 2        #0010
# FULL_AND_FIRST = 3    #0011
#
# FIRST_NAME in FULL_NAME => False
# FIRST_NAME in FULL_AND_FIRST => True
#
# NONE will have no flags are set, and as such all other members will
# contain NONE.
class Names(Flag):
    NONE = 0                                        # 0000 
    FULL_NAME = 1                                   # 0001
    FIRST_NAME = 2                                  # 0010
    FULL_AND_FIRST = FULL_NAME | FIRST_NAME         # 0011
    LAST_NAME = 4                                   # 0100
    FULL_AND_LAST = FULL_NAME | LAST_NAME           # 0101
    FIRST_AND_LAST = FIRST_NAME | LAST_NAME         # 0110
    ALL_NAMES = FULL_NAME | FIRST_NAME | LAST_NAME  # 0111

class Character(NamedTuple):
    jp_name: str
    en_name: str

class Rule(NamedTuple):
    title: str
    json_key: str
    is_name: str
    # When True, will use previously tagged version of the text rather
    # than unnecesssarily retagging.
    is_tokenized_replacement: Optional[bool] = False 
    replace_name: Optional[Names] = None
    no_honorifics: Optional[Names] = None

JP_NAME_SEPS = ["・", ""]

class NLP_MTL_Preprocess:
    rules = [
        # title, json_key, is_name, is_tokenized_replacement, replace_name, no_honorifics
        Rule('Special', 'specials', False, False), # non-name term replacement 
        Rule('Basic', 'basic', False, False), # punctuation replacement 
        # Multi-part katakana name replacement, with records in format:
        #
        # en_name (str): jp_name (List[str])
        # "Capella Emerada Lugunica": ["カペラ", "エメラダ", "ルグニカ"],
        # Will try replacement for all name parts, with and without honorifics   
        Rule('Imp Names', 'names', True, True, Names.ALL_NAMES, Names.ALL_NAMES),
        # Multi-part kanji name replacement, with records in format:
        #
        # en_name (str): jp_name (List[str])
        # "Natsuki Subaru": ["菜月", "昴"],
        # Will try replacement for all name parts, with and without honorifics 
        Rule('Remaining Names', 'full-names', True, True, Names.ALL_NAMES, Names.ALL_NAMES),
        Rule('Single Names', 'single-names', True, True, Names.LAST_NAME, Names.LAST_NAME),
        Rule('Name like', 'name-like', True, True, Names.LAST_NAME, Names.NONE),
    ]

    def __init__(self, 
            text:str, 
            tagger:Tagger, 
            replacement_table=None, 
            verbose=False,
            single_kanji_filter=True,
        ):
        self.text = text
        # Initialized prior to a rule where is_tokenized_replacement
        # is True
        self.tagged_text = None 
        self.tagger = tagger
        if not replacement_table:
            replacement_table = {}
        self.replacement_table = replacement_table
        self.total_replacements = 0
        self.verbose = verbose
        # When single_kanji_filter is True, script will not make replacements 
        # for single-kanji names if the kanji is not followed by an honorific,
        # presumably because completely arbitrary single-kanji replacements can 
        # result in unintenionally replacing parts of random words.
        self.single_kanji_filter = single_kanji_filter
        
    def _log(self, text:str):
        if self.verbose:
            print(text)

    def replace_single_word(self, old_word, replacement):
        n = self.text.count(old_word)
        if n == 0:
            return 0
        self.text = self.text.replace(old_word, replacement)
        self.total_replacements += n
        return n 

    def replace_tokenized_phrase(self, old_phrase, replacement):
        n = self.tagged_text.count(old_phrase)
        if n == 0:
            return 0
        replacement_word = Word(replacement, "NA")
        self.tagged_text = self.tagged_text.replace_multi_word_sequence(
            old_phrase, 
            replacement_word
        )
        self.text = str(self.tagged_text)
        self.total_replacements += n
        return n

    def replace_tokenized_single_word(self, old_word, replacement_text):
        n = self.tagged_text.count_word(old_word)
        if n == 0:
            return 0
        self.tagged_text = self.tagged_text.replace_word(
            old_word, 
            replacement_text
        )
        self.text = str(self.tagged_text)
        self.total_replacements += n
        return n

    @classmethod
    def generate_name_list_from_replacement_table(cls, replacement_table) -> List[str]:
        compiled_name_set = set()
        for rule in cls.rules:
            if rule.json_key in replacement_table and rule.is_name:
                for en_name, jp_name in replacement_table[rule.json_key].items():
                    if isinstance(jp_name, list):
                        for name_part in jp_name:
                            compiled_name_set.add(name_part)
                    else:
                        compiled_name_set.add(jp_name)
        return list(compiled_name_set)

    @classmethod
    def loop_names(cls, character:Character, replace:Names, honorific:Names):
        jp_names = character.jp_name.split(" ")
        en_names = character.en_name.split(" ")
        try:
            assert len(jp_names)==len(en_names)
        except AssertionError:
            print("Names do not match")
            print(character)
            raise SystemExit(0)
        if Names.FULL_NAME in replace:
            indices = range(len(jp_names))
            # Generates a list of tuples, where each tuple is a sequential
            # subsets of the indices of the jp_names/en_names lists 
            # corresponding to all 2+ name part strings
            #
            # ex. ["Wilhelm", "van", "Astrea"] would generate the
            # tuples [(0, 1), (0, 2), (1, 2), (0, 1, 2)] corresponding
            # to the names ["Wilhelm van", "Wilhelm Astrea",
            # "van Astrea", "Wilhelm van Astrea"]
            #
            # Note that since this only generates the indices for 
            # 2+ name part strings, the individual name parts will
            # not be replaced (ie. "Wilhelm" by itself). This is
            # partially remediated by having the Names.FIRST_NAME and 
            # Names.LAST_NAME replacements below, which in this example
            # would replace "Wilhelm" and "Astrea". However, the middle
            # names for 3+ part names will not be replaced in isolation
            # (ie. "van" by itself will not be replaced).
            combinations = list(
                itertools.chain(
                    *[itertools.combinations(indices, i)
                      for i in range(2, len(indices)+1)]))
            for comb in combinations:
                for sep in JP_NAME_SEPS:
                    yield (
                        " ".join([en_names[i] for i in comb]),
                        sep.join([jp_names[i] for i in comb]),
                        Names.FULL_NAME in honorific
                    )
        if Names.FIRST_NAME in replace:
            yield (en_names[0],
                   f'{jp_names[0]}',
                   Names.FIRST_NAME in honorific)
        if Names.LAST_NAME in replace:
            yield (en_names[-1],
                   f'{jp_names[-1]}',
                   Names.LAST_NAME in honorific)


    def replace_name(self, 
                character: Character, 
                replace: Names, 
                no_honorific: Names, 
                replaced_names: dict
            ):
        for en_name, jp_name, no_honor in self.loop_names(character, replace, no_honorific):
            if jp_name in replaced_names:
                continue
            honorifics_replacement_counts = dict()
            honorifics_replacements = self.replacement_table.get('honorifics')
            if honorifics_replacements is not None:
                # The replacement table contains honorifics in the format:
                #
                # jp_honorific (str): en_honorific (str)
                # "先輩": "senpai"
                for jp_honorific, en_honorific in honorifics_replacements.items():
                    honorifics_replacement_counts[en_honorific] = self.replace_tokenized_phrase(
                        f'{jp_name}{jp_honorific}',
                        f'{en_name}-{en_honorific}'
                    )
            # The presence of honorifics is a good sanity check for whether the
            # string being replaced is a name or not. If there are no honorifics
            # and single_kanji_filter is True, single kanji names will not be
            # replaced, presumably because of the greater risk of false-positive
            # replacements
            if no_honor:
                if len(jp_name) > 1:
                    honorifics_replacement_counts['NA'] = self.replace_tokenized_phrase(jp_name, en_name)
                elif not self.single_kanji_filter:
                    # Allow replacing single kanji words that have been tagged
                    # as being proper nouns.
                    honorifics_replacement_counts['NA'] = self.replace_tokenized_single_word(
                        Word(jp_name, PartOfSpeech.PROPER_NOUN),
                        en_name
                    )
            total = sum(honorifics_replacement_counts.values())
            replaced_names[jp_name] = total
            if total > 0: 
                replaced_honorifics_str = ", ".join([
                    f'{honorific}-{replacement_count}' for honorific, replacement_count 
                    in honorifics_replacement_counts.items() if replacement_count > 0
                ])
                self._log(f'    {en_name} :{total} ({replaced_honorifics_str})')

    def replace(self) -> str:
        replaced_names = dict()
        # time_start = time.time()
        prev_rule = None
        for rule in NLP_MTL_Preprocess.rules:
            prev_count = self.total_replacements
            self._log(f'* {rule.title} Replacements:')
            if rule.json_key in self.replacement_table:
                # Retag text after each non-tokenized replacement, as
                # rules that directly modify self.text won't be 
                # in self.tagged_text
                if rule.is_tokenized_replacement:
                    self._log("Starting tokenized replace rule")
                    if not self.tagged_text or \
                       not prev_rule or \
                       not prev_rule.is_tokenized_replacement:
                        self._log("No valid tagged text found. Tagging text.")
                        self.tagged_text = self.tagger.tag(self.text)
                        self._log("Tagged text.")
                    else:
                        self._log("Valid tagged text found.")
                if rule.is_name:
                    # The replacement table contains the names of characters 
                    # with a single name in the format:
                    #
                    # en_name (str): jp_name (str)
                    # "Aldebaran": "アルデバラン",
                    #
                    # The replacement table contains the names of characters 
                    # with multi-part names in the format:
                    #
                    # en_name (str): jp_name (List[str])
                    # "Capella Emerada Lugunica": ["カペラ", "エメラダ", "ルグニカ"],
                    for en_name, jp_name in self.replacement_table[rule.json_key].items():
                        # If jp_name is a list of multiple name parts, combine 
                        # them into a single space-delimited string
                        if isinstance(jp_name, list):
                            jp_name = " ".join(jp_name)
                        char = Character(jp_name, en_name)
                        self.replace_name(char, rule.replace_name, rule.no_honorifics, replaced_names)
                else:
                   for old_word, replacement in self.replacement_table[rule.json_key].items():
                        n = self.replace_single_word(old_word, replacement)
                        if n > 0:
                            self._log(f'    {old_word} → {replacement}:{n}')
            prev_rule = rule
            self._log(f'  SubTotal: {self.total_replacements-prev_count}')

        # time_end = time.time()
        # print(f'Total Replacements: {self.total_replacements}')
        # print(f'Time Taken: {time_end-time_start} seconds')
        return self.text
