from typing import Union
import deepl
from loguru import logger

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException

# Google Cloud
from google.cloud import texttospeech
from google.cloud import translate


from appconfig import AppConfig
import api_keys
from nlp_modules.kairyou_preprocessor import Kairyou
from custom_modules import utilities
from db_management import JishoParseDBM, DeepLDBM, TextToSpeechDBM, GoogleTLDBM

class ApiKeyHandler:

    @staticmethod
    def get_deepl_api_key() -> str:
        return api_keys.deepl_api_key


class Transmute:
    logger.add(sink=AppConfig.rekai_log_path)

    # Jisho web scrape and parse
    @staticmethod
    def parse_string_with_jisho(input_string: str,
                                timestamp: int,
                                progress_monitor: utilities.ProgressMonitor,
                                index: int = 0,
                                total_count: int = 0) -> tuple[str, str]:

        """DOCSTRING PENDING"""

        if AppConfig.MANUAL_RUN_STOP or AppConfig.GLOBAL_RUN_STOP:
            return  # type: ignore

        options = AppConfig.ChromeOptions.options
        driver = webdriver.Chrome(options=options)

        jisho_parsed_html_element = str()

        url = f'https://jisho.org/search/{input_string}'

        try:

            logger.info(f'Trying to parse line {index} out of {total_count}')

            driver.get(url=url)
            logger.info(f'Webdriver instance Started for {index} started')

            zen_bar_element = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.ID, "zen_bar")))
            zen_outer_html = zen_bar_element.get_attribute('outerHTML')

            # Selenium also extracts linebreaks that mess with the html when assigned to a string_list
            zen_html = str(zen_outer_html).replace('\n', "").strip()

            jisho_parsed_html_element += zen_html

        except Exception as e:
            logger.error(f'An exception occured in jisho parse - f{input_string}')
            zen_html = f'<p></p>'
            jisho_parsed_html_element += zen_html

        driver.quit()

        jisho_parsed_html_element = jisho_parsed_html_element.replace('/search/', 'https://jisho.org/search/')
        jisho_parsed_html_element = jisho_parsed_html_element.replace('class="current"', 'class=""')
        jisho_parsed_html_element = jisho_parsed_html_element.replace('class=""', 'class="jisho-link"')

        db_interface = JishoParseDBM()
        db_interface.insert(raw_line=input_string, transmuted_data=jisho_parsed_html_element, unix_timestamp=timestamp)

        progress_monitor.mark_completion()

        return (input_string, jisho_parsed_html_element)

    # DeepL API translation
    @staticmethod
    def translate_string_with_deepl_api(input_string: str,
                                        timestamp: int,
                                        progress_monitor: utilities.ProgressMonitor,
                                        index: int = 0,
                                        total_count: int = 0) -> tuple[str, str]:

        """DOCSTRING PENDING"""


        if AppConfig.MANUAL_RUN_STOP or AppConfig.GLOBAL_RUN_STOP:
            return  # type: ignore

        source_lang = AppConfig.DeeplTranslateConfig.source_language_code
        target_lang = AppConfig.DeeplTranslateConfig.target_language_code

        translator = deepl.Translator(auth_key=ApiKeyHandler.get_deepl_api_key())

        logger.info(f'CALLING_DEEPL_API: Line {index} of {total_count}: {input_string}')

        response = translator.translate_text(text=input_string, source_lang=source_lang, target_lang="EN-US")

        result = response.text

        db_interface = DeepLDBM()
        db_interface.insert(raw_line=input_string, transmuted_data=result, unix_timestamp=timestamp)

        progress_monitor.mark_completion()

        return (input_string, result)

    # Google Cloud Translate API
    @staticmethod
    def translate_string_with_google_tl_api(input_string: str,
                                            timestamp: int,
                                            progress_monitor: utilities.ProgressMonitor,
                                            index: int = 0,
                                            total_count: int = 0) -> tuple[str, str]:

        """DOCSTRING PENDING
        This API expects a single string within a list.
        """


        if AppConfig.MANUAL_RUN_STOP or AppConfig.GLOBAL_RUN_STOP:
            return  # type: ignore

        source_lang = AppConfig.GoogleTranslateConfig.source_language_code
        target_lang = AppConfig.GoogleTranslateConfig.target_language_code
        location = AppConfig.GoogleTranslateConfig.location
        project_id = api_keys.google_project_id
        parent = f"projects/{project_id}/locations/{location}"

        client = translate.TranslationServiceClient()

        logger.info(f'CALLING_GCLOUD_Translate_API: Line {index} of {total_count}: {input_string}')

        response = client.translate_text(
            request={
                "parent": parent,
                "contents": [input_string],
                "mime_type": "text/plain",
                "source_language_code": source_lang,
                "target_language_code": target_lang,
            }
        )

        result = [translation.translated_text for translation in response.translations]

        if len(result) == 1:
            result = str(result[0])
        else:
            result = ''.join(result)

        progress_monitor.mark_completion()

        db_interface = GoogleTLDBM()
        db_interface.insert(raw_line=input_string, transmuted_data=result, unix_timestamp=timestamp)

        progress_monitor.mark_completion()

        return (input_string, result)

    # Google Cloud Text-to-Speech
    @staticmethod
    def tts_string_with_google_api(input_string: str,
                                   timestamp: int,
                                   progress_monitor: utilities.ProgressMonitor,
                                   index: int = 0,
                                   total_count: int = 0) -> tuple[str, str]:

        """DOCSTRING PENDING"""

        progress_monitor.mark_completion()

        progress_monitor.mark_completion()

        progress_monitor.mark_completion()

        if AppConfig.MANUAL_RUN_STOP or AppConfig.GLOBAL_RUN_STOP:
            return  # type: ignore

        # Get configration on run
        language_code: str = AppConfig.GoogleTTSConfig.language_code
        voice_name: str = AppConfig.GoogleTTSConfig.voice_name
        audio_encoding = AppConfig.GoogleTTSConfig.audio_encoding
        speaking_rate: float = AppConfig.GoogleTTSConfig.speaking_rate
        pitch: float = AppConfig.GoogleTTSConfig.pitch
        volume_gain_db: float = AppConfig.GoogleTTSConfig.volume_gain_db

        tts_client = texttospeech.TextToSpeechClient(
            client_options={"api_key": api_keys.google_cloud_api_key, "quota_project_id": api_keys.google_project_id}
        )
        input_for_synthesis = texttospeech.SynthesisInput({"text": f"{input_string}"})
        voice_settings = texttospeech.VoiceSelectionParams(
            {
                "language_code": language_code,
                "name": voice_name
            }
        )
        audio_configuration = texttospeech.AudioConfig(
            {
                "audio_encoding": audio_encoding,
                "speaking_rate": speaking_rate,
                "pitch": pitch,
                "volume_gain_db": volume_gain_db,
            }
        )

        logger.info(f'CALLING_GCLOUD_TTS_API: Line {index} of {total_count}: {input_string}')

        response = tts_client.synthesize_speech(
            input=input_for_synthesis,
            voice=voice_settings,
            audio_config=audio_configuration)

        result = utilities.encode_bytes_to_base64_string(response.audio_content)

        db_interface = TextToSpeechDBM()
        db_interface.insert(raw_line=input_string, transmuted_data=result, unix_timestamp=timestamp)

        progress_monitor.mark_completion()

        return (input_string, result)

    @staticmethod
    def preprocess_with_kairyou(input_string: str, input_replacements_dict: dict):
        preprocessor = Kairyou(text_to_preprocess=input_string, replacements_json=input_replacements_dict)
        preprocessor.preprocess()
        output = preprocessor.text_to_preprocess
        return output

    @staticmethod
    def post_process_dialogue(input_string: str, *args):
        """Replaces quotation/japanese quotation marks with []"""

        opening_characters = {"\"", "「"}
        closing_characters = {"\"", "」"}

        if input_string[0] in opening_characters:
            output_string = "[" + input_string[1:]
        else:
            output_string = input_string

        if input_string[-1] in closing_characters:
            output_string = output_string[:-1] + "]"
        else:
            output_string = output_string

        return output_string
