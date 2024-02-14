## built-in libraries
import os

## third-party libraries
from google.cloud import texttospeech
from selenium.webdriver.chrome.options import Options

## custom modules
from dataclasses import dataclass


@dataclass
class AppConfig:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """This class method ensures that only one instance of the class exists"""
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
        return cls._instance

    ##========== FLAGS =============================##

    ENABLE_TIMING: bool = False  # Used by timing wrapper in utilities

    # Debugging Controls
    STOP_RUN_IF_TEXT_PROCESSING_ERRORS: bool = False

    # Global Stop Flag
    GLOBAL_RUN_STOP: bool = False

    # Manual Cancel Flag
    MANUAL_RUN_STOP: bool = False

    ##=========== PATHS AND DIRECTORIES =============##
    # current working directory
    current_working_directory = os.getcwd()

    # paths and variables pertaining to logging
    logging_directory: str = os.path.join(current_working_directory, 'logs')
    deep_log_transmutors: bool = True
    deep_log_databases: bool = False
    deep_log_dataclasses: bool = False

    # paths to dictionary files
    dictionary_directory: str = os.path.join(current_working_directory, 'dictionaries')

    # path to replacement json
    path_to_replacements_json: str = os.path.join(dictionary_directory, 'replacements.json')

    # paths pertaining to databases
    datastores_directory: str = os.path.join(current_working_directory, 'datastores')
    jisho_parse_db_path: str = os.path.join(datastores_directory, 'jisho_parse.db')
    deepl_tl_db_path: str = os.path.join(datastores_directory, 'deepl_tl.db')
    google_tl_db_path: str = os.path.join(datastores_directory, 'google_tl.db')
    je_tts_db: str = os.path.join(datastores_directory, 'je_text_to_speech.db')
    openai_gpt_db_path: str = os.path.join(datastores_directory, 'openai_gpt')

    # path to the system database
    sys_directory: str = os.path.join(current_working_directory, 'sys')
    system_db_path: str = os.path.join(sys_directory, 'system.db')

    # Path to CSS and JS source files
    path_to_css_source = os.path.join(current_working_directory, 'html_src', 'css', 'styles.css')
    path_to_js_source = os.path.join(current_working_directory, 'html_src', 'javascript', 'rekai.js')

    # paths pertaining to generator outputs
    output_directory = os.path.join(current_working_directory, 'outputs')
    path_to_rekai_html_src = os.path.join(current_working_directory, 'html_src')

    ##=========== INTERNAL PARAMETERS =============##
    # concurrency limits
    # Right now all processors use asyncio. These settings will be deprecated.
    parallel_process: bool = True
    general_multithread_max_workers: int = 6

    # Chunk size for APIs that accept chunks of text - Eg: Google TL v2
    transmutor_chunk_size: int = 20

    # text to speech configuration
    tts_file_extension: str = 'opus'
    tts_output_folder_name: str = 'tts_files'

    class GoogleTTSConfig:
        language_code: str = 'ja-JP'
        # ssml_gender = texttospeech.SsmlVoiceGender.NEUTRAL # Not all voices support this
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

    class OpenAIConfig:
        model: str = 'gpt-3.5-turbo-0125'
        temperature: float = 1
        top_p: int = 1
        n: int = 1
        stream: bool = False



@dataclass
class RunConfig:

    _instances = []

    # This class is called by default by RekaiText.
    run_timestamp: int

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
                 run_tts=True,
                 run_deepl_tl=True,
                 run_google_tl=True,
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
                 use_preprocessed_for_google_tl=True,

                 also_output_single_file=False,
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

        self.run_timestamp = unix_timestamp

        RunConfig._instances.append(self)

    @classmethod
    def get_all_instances(cls):
        return cls._instances


app_config = AppConfig()
def config_object_to_dict(config_object):
    return {key: getattr(config_object, key) for key in dir(config_object) if not key.startswith('_') and not callable(getattr(config_object, key))}

def update_config_from_dict(config_dict, config_obect):
    for key, value in config_dict.items():
        setattr(config_obect, key, value)
    return config_obect

print(config_object_to_dict(app_config))