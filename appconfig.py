import os

from google.cloud import texttospeech
from dataclasses import dataclass
from selenium.webdriver.chrome.options import Options


@dataclass
class AppConfig:
    _instance = None

    global_run_stop: bool = False

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

    # Path to CSS and JS source files
    path_to_css_source = os.path.join(current_working_directory, 'html_src', 'css', 'styles.css')
    path_to_js_source = os.path.join(current_working_directory, 'html_src', 'javascript', 'rekai.js')

    # paths pertaining to generator outputs
    output_directory = os.path.join(current_working_directory, 'outputs')
    path_to_rekai_html_src = os.path.join(current_working_directory, 'html_src')

    ##=========== INTERNAL PARAMETERS =============##
    # concurrency limits
    # Right now all processors use asyncio. These settings will be deprecated.
    general_multipro_max_workers: int = 8
    jisho_multipro_max_workers: int = 16
    deepl_multipro_max_workers: int = 4
    tts_multipro_max_workers: int = 16

    # text to speech configuration
    tts_file_extension: str = 'opus'
    tts_output_folder_name: str = 'tts_files'

    class GoogleTTSConfig:
        language_code: str = 'ja-JP'
        # ssml_gender = texttospeech.SsmlVoiceGender.NEUTRAL # Not all voices support this flag
        voice_name: str = 'ja-JP-Neural2-B'
        audio_encoding = texttospeech.AudioEncoding.OGG_OPUS
        speaking_rate: float = 0.9
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
    run_id: int

    preprocess: bool
    use_preprocessed_for_paragraphs: bool
    run_jisho_parse: bool
    run_tts: bool
    run_deepl_tl: bool
    run_google_tl: bool
    run_gpt4_analysis: bool
    clean_post_split: bool

    include_jisho_parse: bool
    include_clause_analysis: bool

    deepl_tl_paragraphs: bool
    deepl_tl_lines: bool
    deepl_tl_clauses: bool
    use_preprocessed_for_deepl_tl: bool

    google_tl_paragraphs: bool
    google_tl_lines: bool
    google_tl_clauses: bool
    use_preprocessed_for_google_tl: bool

    output_single_file: bool

    def __init__(self,
                 unix_timestamp: int,

                 preprocess=True,
                 use_preprocessed_for_paragraphs=True,
                 run_jisho_parse=True,
                 run_tts=False,
                 run_deepl_tl=False,
                 run_google_tl=False,
                 run_gpt4_analysis=False,
                 clean_post_split=True,

                 include_jisho_parse=True,
                 include_clause_analysis=True,

                 deepl_tl_paragraphs=False,
                 deepl_tl_lines=True,
                 deepl_tl_clauses=True,
                 use_preprocessed_for_deepl_tl=True,

                 google_tl_paragraphs=False,
                 google_tl_lines=True,
                 google_tl_clauses=True,
                 use_preprocessed_for_google_tl = True,

                 also_output_single_file = False,
                 ):

        self.preprocess = preprocess
        self.use_preprocessed_for_paragraphs = preprocess and use_preprocessed_for_paragraphs
        self.run_jisho_parse = run_jisho_parse
        self.run_tts = run_tts
        self.run_deepl_tl = run_deepl_tl
        self.run_google_tl = run_google_tl
        self.run_gpt4_analysis = run_gpt4_analysis
        self.clean_post_split = clean_post_split

        self.include_jisho_parse = include_jisho_parse and run_jisho_parse
        self.include_clause_analysis = include_clause_analysis

        self.deepl_tl_paragraphs = deepl_tl_paragraphs and run_deepl_tl
        self.deepl_tl_lines = deepl_tl_lines and run_deepl_tl
        self.deepl_tl_clauses = deepl_tl_clauses and run_deepl_tl
        self.use_preprocessed_for_deepl_tl = preprocess and use_preprocessed_for_deepl_tl

        self.google_tl_paragraphs = google_tl_paragraphs and run_google_tl
        self.google_tl_lines = google_tl_lines and run_google_tl
        self.google_tl_clauses = google_tl_clauses and run_google_tl
        self.use_preprocessed_for_google_tl = preprocess and use_preprocessed_for_google_tl

        self.output_single_file = also_output_single_file

        self.run_id = unix_timestamp

