import os

from google.cloud import texttospeech
from dataclasses import dataclass
from selenium.webdriver.chrome.options import Options


@dataclass
class AppConfig:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """This class method ensures that only one instance of the class exists"""
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
        return cls._instance

    ##=========== PATHS AND DIRECTORIES =============##
    # current working directory
    current_working_directory = os.getcwd()

    # paths and variables pertaining to logging
    logging_directory: str = os.path.join(current_working_directory, 'logs')
    rekai_log_path: str = os.path.join(logging_directory, 'rekai_log.log')
    db_log_path: str = os.path.join(logging_directory, 'db_log.log')
    deep_log_databases: bool = False
    dataclasses_log_path: str = os.path.join(logging_directory, 'dataclasses.log')
    deep_log_dataclasses: bool = False

    # paths to dictionary files
    dictionary_directory: str = os.path.join(current_working_directory, 'dictionaries')
    path_to_katakana_words: str = os.path.join(dictionary_directory, 'katakana_words.txt')

    # path to replacement json
    path_to_replacements_json: str = os.path.join(dictionary_directory, 'replacements.json')

    # paths pertaining to databases
    datastores_directory: str = os.path.join(current_working_directory, 'datastores')
    jisho_parse_db_path: str = os.path.join(datastores_directory, 'jisho_parse.db')
    deepl_tl_db_path: str = os.path.join(datastores_directory, 'deepl_tl.db')
    google_tl_db_path: str = os.path.join(datastores_directory, 'google_tl.db')
    je_tts_db: str = os.path.join(datastores_directory, 'je_text_to_speech.db')
    translations_db_path: str = os.path.join(datastores_directory, 'translations.db')

    # paths pertaining to generator outputs
    output_directory = os.path.join(current_working_directory, 'outputs')
    path_to_rekai_html_src = os.path.join(current_working_directory, 'html_src')

    ##=========== INTERNAL PARAMETERS =============##
    # concurrency limits
    general_multipro_max_workers: int = 8
    jisho_multipro_max_workers: int = 16
    deepl_multipro_max_workers: int = 4
    tts_multipro_max_workers: int = 16

    # text to speech configuration
    tts_file_extension: str = 'opus'
    tts_output_folder_name: str = 'tts_files'

    class GoogleTTSConfig:
        language_code: str = 'ja-JP'
        ssml_gender = texttospeech.SsmlVoiceGender.NEUTRAL
        voice_name: str = 'ja-JP-Wavenet-B'
        audio_encoding = texttospeech.AudioEncoding.OGG_OPUS
        speaking_rate: float = 1.0
        pitch: float = 0.0
        volume_gain_db: float = 0.0

    class GoogleTranslateConfig:
        source_language_code: str = 'ja-JP'
        target_language_code: str = 'en_US'
        location: str = 'global'

    class DeeplTranslateConfig:
        source_language_code: str = 'JA'
        target_language_code: str = 'EN_US'

    # Selenium Webdriver configuration
    class ChromeOptions:
        options = Options()
        options.add_argument('--headless')
        # user_profile_path = ""
        # options.setBinary('/path/to/chrome/binary')
        # PROFILES ARE NOT WORKING RIGHT NOW
        # options.add_argument(f'--user-data-dir={user_profile_path}')


@dataclass
class RunConfig:
    # This class is called by default by RekaiText.
    preprocess: bool
    run_jisho_parse: bool
    run_tts: bool

    def __init__(self,
                 preprocess=True,
                 run_jisho_parse=True,
                 run_tts=True,
                 run_deepl_tl=True):

        self.preprocess: bool = preprocess
        self.run_jisho_parse: bool = run_jisho_parse
        self.run_tts: bool = run_tts
        self.run_deepl_tl: bool = run_deepl_tl
