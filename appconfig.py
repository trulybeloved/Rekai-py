## built-in libraries
import os

## third-party libraries
from google.cloud import texttospeech

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

    # Transmute Failure
    TRANSMUTE_FAILURE: bool = False

    ##=========== PATHS AND DIRECTORIES =============##
    # current working directory
    current_working_directory = os.getcwd()

    ## secrets are under appdata on windows, and under .config on linux
    if(os.name == 'nt'):  ## Windows
        secrets_dir = os.path.join(os.environ['APPDATA'],"RekaiSecrets")
    else:  ## Linux
        secrets_dir = os.path.join(os.path.expanduser("~"), ".config", "RekaiSecrets")

    # paths and variables pertaining to logging
    logging_directory: str = os.path.join(current_working_directory, 'logs')
    deep_log_transmutors: bool = False
    deep_log_databases: bool = False
    deep_log_dataclasses: bool = False

    # paths to dictionary files
    dictionary_directory: str = os.path.join(current_working_directory, 'dictionaries')

    # path to replacement json
    path_to_kairyou_replacements_json: str = os.path.join(dictionary_directory, 'preprocessor_replacement_tables', 'kairyou_rezero_replacements.json')
    path_to_fukuin_replacements_json: str = os.path.join(dictionary_directory, 'preprocessor_replacement_tables', 'fukuin_rezero_replacements.json')

    # default preprocessor
    default_preprocessor: str = 'fukuin'  # Can be 'kairyou'

    # paths pertaining to databases
    datastores_directory: str = os.path.join(current_working_directory, 'datastores')
    jisho_parse_db_path: str = os.path.join(datastores_directory, 'jisho_parse.db')
    deepl_tl_db_path: str = os.path.join(datastores_directory, 'deepl_tl.db')
    google_tl_db_path: str = os.path.join(datastores_directory, 'google_tl.db')
    je_tts_db: str = os.path.join(datastores_directory, 'je_text_to_speech.db')
    openai_gpt_db_path: str = os.path.join(datastores_directory, 'openai_gpt.db')
    gemini_gpt_db_path: str = os.path.join(datastores_directory, 'gemini_gpt.db')
    testing_db_path: str = os.path.join(datastores_directory, 'test.db')
    autorun_db_path: str = os.path.join(datastores_directory, 'autorun.db')

    # path to the system database
    sys_directory: str = os.path.join(current_working_directory, 'sys')
    system_db_path: str = os.path.join(sys_directory, 'system.db')

    # Path to CSS and JS source files
    path_to_css_source = os.path.join(current_working_directory, 'html_src', 'css', 'styles.css')
    path_to_js_source = os.path.join(current_working_directory, 'html_src', 'javascript', 'rekai.js')

    # paths pertaining to generator outputs
    output_directory = os.path.join(current_working_directory, 'outputs')
    path_to_rekai_html_src = os.path.join(current_working_directory, 'html_src')

    ## api keys and credentials
    
    deepl_api_key_path = os.path.join(secrets_dir, "deepl_api_key.txt")
    openai_api_key_path = os.path.join(secrets_dir,'openai_api_key.txt')
    gemini_api_key_path = os.path.join(secrets_dir, 'gemini_api_key.txt')

    ##=========== Path Creation =============##

    ## for the secrets directory and the api key files
    if(os.path.isdir(secrets_dir) == False):
        os.mkdir(secrets_dir)

    if(os.path.exists(deepl_api_key_path) == False):
        with open(deepl_api_key_path, 'w') as f:
            f.truncate(0)

    if(os.path.exists(openai_api_key_path) == False):

        with open(openai_api_key_path, 'w') as f:
            f.truncate(0)

    ##=========== INTERNAL PARAMETERS =============##
    # backoff-retry parameters
    backoff_max_tries: int = 3
    backoff_max_time: int = 20

    # concurrency limits

    # the python default is  min(32, os.cpu_count() + 4).
    # os.cpu_count() returns total number of logical processors and not number of physical cpu cores, and can actually return None on some systems
    cpu_count = os.cpu_count()
    general_multithread_max_workers: int = min(4, cpu_count + 1) if cpu_count is not None else 4
    async_webscrape_semaphore_value: int = 15

    # Chunk size for APIs that accept chunks of text - Eg: Google TL v2
    default_transmutor_chunk_size: int = 20
    deepl_transmutor_chunk_size: int = 30
    google_tl_transmutor_chunk_size: int = 30

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
        target_language_code: str = 'EN-US'

    # Selenium Webdriver configuration

    class OpenAIConfig:
        model: str = 'gpt-3.5-turbo'
        temperature: float = 1
        top_p: int = 1
        n: int = 1
        stream: bool = False

    class GeminiConfig:
        model: str = 'gemini-1.5-pro-latest'
        # model: str = 'gemini-pro'
        temperature: float = 0.5
        top_p: float = 0.95
        top_k: int = 1
        stream: bool = False


class FukuinConfig:

    cwd = AppConfig.current_working_directory

    tokenizer = "spacy"  # "spacy" / "sudachi" / "fugashi"
    tag_potential_proper_nouns = True
    use_user_dict = True  # SHOULD ALWAYS BE TRUE
    user_dic_path = os.path.join(cwd, 'nlp_modules', 'kroatoanjp_fukuin', 'data', 'dictionaries', 'rezero-sudachi.dic')
    use_single_kanji_filter = True  # SHOULD BE TRUE UNLESS REPLACING SINGLE KANJI NAMES
    katakana_words_file_path = os.path.join(cwd, 'nlp_modules', 'kroatoanjp_fukuin', 'data', 'katakana_words.txt')


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

    # parameters used internally
    preprocessed_provided = False

    def __init__(self,
                 unix_timestamp: int,

                 preprocess=True,
                 use_preprocessed_for_paragraphs=True,
                 run_jisho_parse=True,
                 run_tts=False,
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
    return {key: getattr(config_object, key) for key in dir(config_object) if
            not key.startswith('_') and not callable(getattr(config_object, key))}

def update_config_from_dict(config_dict, config_object):
    for key, value in config_dict.items():
        setattr(config_object, key, value)
    return config_object

