import os
from google.cloud import texttospeech
from dataclasses import dataclass
@dataclass
class AppConfig:

    _instance = None
    def __new__(cls, *args, **kwargs):
        """This class method ensures that only one instance of the class exists"""
        if cls._instance is None:
            cls._instance = super(AppConfig, cls).__new__(cls)
        return cls._instance

    current_working_directory = os.getcwd()
    jisho_parse_db_path = os.path.join(current_working_directory, 'datastores', 'jisho_parse.db')
    deepl_tl_db_path = os.path.join(current_working_directory, 'datastores', 'deepl_tl.db')
    je_tts_db = os.path.join(current_working_directory, 'datastores', 'je_text_to_speech.db')

    class GoogleTTSConfig:

        language_code: str = 'ja-JP'
        ssml_gender = texttospeech.SsmlVoiceGender.NEUTRAL
        voice_name: str = 'ja-JP-Wavenet-B'
        audio_encoding = texttospeech.AudioEncoding.OGG_OPUS
        speaking_rate: float = 1.0
        pitch: float = 0.0
        volume_gain_db: float = 0.0

