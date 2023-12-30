import os

class AppConfig:

    current_working_directory = os.getcwd()
    jisho_parse_db_path = os.path.join(current_working_directory, 'datastores', 'jisho_parse.db')
    deepl_tl_db_path = os.path.join(current_working_directory, 'datastores', 'deepl_tl.db')
    je_tts_db = os.path.join(current_working_directory, 'datastores', 'je_text_to_speech.db')
