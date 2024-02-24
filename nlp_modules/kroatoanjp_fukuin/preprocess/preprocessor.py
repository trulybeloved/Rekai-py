#!/usr/bin/env python

import json
import typing

from nlp_modules.kroatoanjp_fukuin.preprocess.nlp_mtl_preprocess import (NLP_MTL_Preprocess)
from nlp_modules.kroatoanjp_fukuin.preprocess.mtl_preprocess import MTL_Preprocess
from nlp_modules.kroatoanjp_fukuin.preprocess.tokenizer.fugashi_tokenizer import FugashiTokenizer
from nlp_modules.kroatoanjp_fukuin.preprocess.tokenizer.sudachi_tokenizer import SudachiTokenizer
from nlp_modules.kroatoanjp_fukuin.preprocess.tokenizer.spacy_tokenizer import SpacyTokenizer
from nlp_modules.kroatoanjp_fukuin.preprocess.tagger import Tagger
from nlp_modules.kroatoanjp_fukuin.preprocess.tools.mecab_dict_generator import MecabDictGenerator
from nlp_modules.kroatoanjp_fukuin.preprocess.tools.sudachi_dict_generator import SudachiDictGenerator
from nlp_modules.kroatoanjp_fukuin.preprocess.fukuin_config import FukuinConfig


def load_replacement_table(filename):
    with open(filename, "r", encoding='utf-8') as replacement_json_file:
        replacement_table = json.loads(replacement_json_file.read())
    return replacement_table


def run_basic_mtl_preprocessor(input_string: str, path_to_replacements_table: str) -> str:
    preprocess = MTL_Preprocess(
        text=input_string,
        replacement=path_to_replacements_table,
        verbose=False,
        single_kanji_filter=FukuinConfig.use_single_kanji_filter
    )
    preprocessed_text = preprocess.replace()
    return preprocessed_text


def run_nlp_mtl_preprocessor(
        input_string: str,
        path_to_replacements_table: str,
        tokenizer: typing.Union[FugashiTokenizer, SudachiTokenizer, SpacyTokenizer] = None,
        verbose: bool = False) -> str:
    if not tokenizer:
        if FukuinConfig.tokenizer == "fugashi":
            if FukuinConfig.use_user_dict:
                tokenizer = FugashiTokenizer(user_dic_path=FukuinConfig.user_dic_path)
            else:
                tokenizer = FugashiTokenizer()
        elif FukuinConfig.tokenizer == "sudachi":
            if FukuinConfig.use_user_dict:
                tokenizer = SudachiTokenizer(user_dic_path=FukuinConfig.user_dic_path)
            else:
                tokenizer = SudachiTokenizer()
        elif FukuinConfig.tokenizer == "spacy":
            if FukuinConfig.use_user_dict:
                tokenizer = SpacyTokenizer(user_dic_path=FukuinConfig.user_dic_path)
            else:
                tokenizer = SpacyTokenizer()
        else:
            raise ValueError(f"Received unexpected tokenizer: {FukuinConfig.tokenizer}")

    replacement_table = load_replacement_table(path_to_replacements_table)
    proper_noun_list = NLP_MTL_Preprocess.generate_name_list_from_replacement_table(replacement_table)
    tagger = Tagger(
        tokenizer=tokenizer,
        tag_potential_proper_nouns=FukuinConfig.tag_potential_proper_nouns,
        proper_noun_list=proper_noun_list,
    )
    preprocess = NLP_MTL_Preprocess(
        text=input_string,
        tagger=tagger,
        replacement_table=replacement_table,
        verbose=verbose,
        single_kanji_filter=FukuinConfig.use_single_kanji_filter
    )
    preprocessed_text = preprocess.replace()

    return preprocessed_text


def build_mecab_dict(args):
    replacement_table = load_replacement_table(args.replacement_json)
    dict_generator = MecabDictGenerator(
        dictionary_type=args.dictionary_type,
        dictionary_source_directory=args.dictionary_source_directory,
        replacement_table=replacement_table
    )
    dict_generator.generate()


def build_sudachi_dict(args):
    replacement_table = load_replacement_table(args.replacement_json)
    dict_generator = SudachiDictGenerator(
        dictionary_source_file=args.dictionary_source_file,
        replacement_table=replacement_table
    )
    dict_generator.generate()
