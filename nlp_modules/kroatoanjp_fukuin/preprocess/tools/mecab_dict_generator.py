import datetime
import os
import subprocess

from nlp_modules.kroatoanjp_fukuin.preprocess.nlp_mtl_preprocess import NLP_MTL_Preprocess
from nlp_modules.kroatoanjp_fukuin.preprocess.utils import is_katakana

DICT_CSV_FOLDER = "generated-mecab-dict-csv"
DICT_OUTPUT_FOLDER = "data/dictionaries"

class MecabDictGenerator:
    def __init__(self, 
            dictionary_type:str, 
            dictionary_source_directory:str, 
            replacement_table
        ):
        self.dictionary_type = dictionary_type
        self.dictionary_source_directory = dictionary_source_directory
        self.replacement_table = replacement_table

    # Generate mecab user dictionary csv of katakana names 
    # from the replacement table
    def _build_mecab_csv(self, outfile_stem):
        print("Extracting katakana names from replacement table")
        csv_rows = []
        name_list = NLP_MTL_Preprocess.generate_name_list_from_replacement_table(self.replacement_table)
        for name in sorted(name_list):
            if is_katakana(name):
                if self.dictionary_type == "unidic":
                    csv_rows.append(f'{name},*,*,1,名詞,固有名詞,一般,*,*,*,{name},{name},{name},{name},{name},{name},固,*,*,*,*,*,*,*,{name},{name},{name},{name},*,*,*,*,*')
                elif self.dictionary_type == "ipadic":
                    csv_rows.append(f"{name},,,1,名詞,固有名詞,一般,*,*,*,{name},{name},{name}")
                else:
                    raise ValueError(f"Received unsupported dictionary type: {self.dictionary_type}")
        print(f"Extracted {len(csv_rows)} katakana names from replacement table")
        if not os.path.exists(DICT_CSV_FOLDER):
            os.mkdir(DICT_CSV_FOLDER)
        csv_file_name = f"{DICT_CSV_FOLDER}/{outfile_stem}.csv"
        with open(csv_file_name, "w") as csv_file:
            csv_file_text = "\n".join(csv_rows)
            csv_file.write(csv_file_text)
        print(f"Wrote {self.dictionary_type} user-dic csv to: {csv_file_name}")
        return csv_file_name

    def generate(self):
        print("Generating new MeCab dictionary")
        timestamp = datetime.datetime.now().isoformat()
        file_stem = f"user-{self.dictionary_type}-{timestamp}"
        csv_file_name = self._build_mecab_csv(file_stem)
        new_dictionary_path = f"{DICT_OUTPUT_FOLDER}/{file_stem}.dic"
        subprocess.run([
            'fugashi-build-dict', "-d", self.dictionary_source_directory, "-u",
            new_dictionary_path,"-f", "utf-8", "-t", "utf-8", csv_file_name
        ])
        print(f"Dictionary written to: {new_dictionary_path}")
