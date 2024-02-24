#!/usr/bin/env python
#   MTL_Preprocess.py
#
#
#   Author      #   thevoidzero#4686
#
#   Purpose     #   Quick preparation of a Chapter’s text for a DeepL run.
#                   Replaces Japanese characters that can mess up the MTL tool, and stuff like character/location/RZ-specific terms.
#
#   PythonVer   #   3.9 (also works with 3.7.6)
#
#   ExtPackages #   None
#
#   Precond     #   Copy-paste entire chapter from the WN website into a separate file.
#
#   CmdLineArg  #   Argument 1 - Path to file with RAW WN chapter
#                   Argument 2 - Path to replacement Json
#
#   Output      #   File with same name as the input file + "-rep", having had the replacements according to
#                   the Json. It should now be ready to be used in DeepL. 

import time

from enum import Flag
from collections import namedtuple
import itertools

class Names(Flag):
    NONE = 0
    FULL_NAME = 1
    FIRST_NAME = 2
    FULL_AND_FIRST = 3
    LAST_NAME = 4
    FULL_AND_LAST = 5 
    FIRST_AND_LAST = 6
    ALL_NAMES = 7


Character = namedtuple('Character', 'jp_name en_name')

JP_NAME_SEPS = ["・", ""]

class MTL_Preprocess:
    def __init__(
            self, 
            text, 
            replacement=None, 
            single_kanji_filter=True,
            verbose=False
        ):
        self.text = text
        if not replacement:
            replacement = {}
        self.rep = replacement
        self.total_replacements = 0
        self.verbose = verbose
        self.single_kanji_filter = single_kanji_filter
        


    def replace_single_word(self, word, replacement):
        n = self.text.count(word)
        if n == 0:
            return 0
        # print(word, n)
        self.text = self.text.replace(word, replacement)
        self.total_replacements += n
        return n


    def loop_names(self, character,
                   replace=Names.FULL_NAME,
                   honorific=Names.ALL_NAMES):
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
            combinations = list(
                itertools.chain(
                    *[itertools.combinations(indices, i)
                      for i in range(2, len(indices)+1)]))
            for comb in combinations:
                for sep in JP_NAME_SEPS:
                    yield (
                        " ".join(map(lambda i: en_names[i], comb)),
                        sep.join(map(lambda i: jp_names[i], comb)),
                        Names.FULL_NAME in honorific
                    )
            # yield (character.en_name,
            #        f'{character.last_jp_name}{character.first_jp_name}',
            #        Names.FULL_NAME in honorific)
            # yield (character.en_name,
            #        f'{character.last_jp_name}・{character.first_jp_name}',
            #        Names.FULL_NAME in honorific)
        if Names.FIRST_NAME in replace:
            yield (en_names[0],
                   f'{jp_names[0]}',
                   Names.FIRST_NAME in honorific)
        if Names.LAST_NAME in replace:
            yield (en_names[-1],
                   f'{jp_names[-1]}',
                   Names.LAST_NAME in honorific)


    def replace_name(self, character,
                     replace=Names.FULL_NAME,
                     no_honorific=Names.ALL_NAMES,
                     replaced_names=list()):
        for nen, njp, no_honor in self.loop_names(character, replace, no_honorific):
            if njp in replaced_names:
                continue
            data = dict()
            for hon, hon_en in self.rep['honorifics'].items():
                data[hon_en] = self.replace_single_word(
                    f'{njp}{hon}',
                    f'{nen}-{hon_en}'
                )
            if no_honor:
                if len(njp) > 1 or not self.single_kanji_filter:
                    data['NA'] = self.replace_single_word(njp, nen)

            total = sum(data.values())
            replaced_names[njp] = total
            if not self.verbose or total == 0:
                continue

            print(f'    {nen} :{total} (', end='')
            print(", ".join(map(lambda x: f'{x}-{data[x]}',
                                filter(lambda x: data[x]>0, data))), end=')\n')

    def replace(self):
        rules = [
            # title, json_key, is_name, replace_name, no_honorifics
            ('Special', 'specials', False),
            ('Basic', 'basic', False),
            ('Imp Names', 'names', True, Names.ALL_NAMES, Names.ALL_NAMES),
            ('Semi Imp Names', 'last-names', True,
             Names.ALL_NAMES, Names.FULL_AND_LAST),
            ('Remaining Names', 'full-names', True,
             Names.ALL_NAMES, Names.FULL_NAME),
            ('Single Names', 'single-names', True, Names.LAST_NAME, Names.LAST_NAME),
            ('Name like', 'name-like', True, Names.LAST_NAME, Names.NONE),
            ('Cleaning Up', 'cleaning-up', False)
        ]

        replaced_names = dict()
        time_start = time.time()
        for rule in rules:
            prev_count = self.total_replacements
            if self.verbose:
                print(f'* {rule[0]} Replacements:')
            if rule[2]:             # if it is a name
                try:
                    for k, v in self.rep[rule[1]].items():
                        if not isinstance(v, list):
                            v = [v]
                        char = Character(" ".join(v), k)
                        self.replace_name(char, rule[3], rule[4], replaced_names)
                except KeyError:
                    continue
            else:
                try:
                    for k, v in self.rep[rule[1]].items():
                        n = self.replace_single_word(k, v)
                        if n > 0:
                            print(f'    {k} → {v}:{n}')
                except KeyError:
                    continue
            print(f'  SubTotal: {self.total_replacements-prev_count}')

        time_end = time.time()
        print(f'Total Replacements: {self.total_replacements}')
        print(f'Time Taken: {time_end-time_start} seconds')
        return self.text
