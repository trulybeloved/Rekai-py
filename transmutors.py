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
from nlp_modules.japanese_nlp import Classifier
import api_keys
from nlp_modules.kairyou_preprocessor import Kairyou

class ApiKeyHandler:

    @staticmethod
    def get_deepl_api_key() -> str:
        return api_keys.deepl_api_key


class Transmute:
    logger.add(sink=AppConfig.rekai_log_path)

    # Jisho web scrape and parse
    @staticmethod
    def parse_string_with_jisho(line: str, index: int = 0, total_count: int = 0) -> tuple[str, str]:

        """DOCSTRING PENDING"""

        options = AppConfig.ChromeOptions.options
        driver = webdriver.Chrome(options=options)

        jisho_parsed_html_element = str()

        if Classifier.contains_no_parsable_ja_text(line):
            jisho_parsed_html_element += 'unparsable'

        else:
            url = f'https://jisho.org/search/{line}'

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
                logger.error(f'An exception occured in jisho parse - f{line}')
                zen_html = f'<p></p>'
                jisho_parsed_html_element += zen_html

            driver.quit()

            jisho_parsed_html_element = jisho_parsed_html_element.replace('/search/', 'https://jisho.org/search/')
            jisho_parsed_html_element = jisho_parsed_html_element.replace('class="current"', 'class=""')
            jisho_parsed_html_element = jisho_parsed_html_element.replace('class=""', 'class="jisho-link"')

        return (line, jisho_parsed_html_element)

    # DeepL API translation
    @staticmethod
    def translate_string_with_deepl_api(line: str, index: int = 0, total_count: int = 0) -> tuple[str, str]:

        """DOCSTRING PENDING"""

        source_lang = AppConfig.DeeplTranslateConfig.source_language_code
        target_lang = AppConfig.DeeplTranslateConfig.target_language_code

        translator = deepl.Translator(auth_key=ApiKeyHandler.get_deepl_api_key())

        result = translator.translate_text(text=line, source_lang=source_lang, target_lang="EN-US")

        return line, result.text

    # Google Cloud Translate API
    @staticmethod
    def translate_string_with_google_tl_api(line: str, index: int = 0, total_count: int = 0) -> tuple[str, str]:

        """DOCSTRING PENDING
        This API can accept a list.
        """

        source_lang = AppConfig.GoogleTranslateConfig.source_language_code
        target_lang = AppConfig.GoogleTranslateConfig.target_language_code
        location = AppConfig.GoogleTranslateConfig.location
        project_id = api_keys.google_project_id
        parent = f"projects/{project_id}/locations/{location}"

        client = translate.TranslationServiceClient()

        response = client.translate_text(
            request={
                "parent": parent,
                "contents": [line],
                "mime_type": "text/plain",
                "source_language_code": source_lang,
                "target_language_code": target_lang,
            }
        )

        result = [translation.translated_text for translation in response.translations]

        if len(result) == 1:
            return line, str(result[0])
        else:
            return line, ''.join(result)

    # Google Cloud Text-to-Speech
    @staticmethod
    def tts_string_with_google_api(line: str, index: int = 0, total_count: int = 0) -> tuple[str, bytes]:

        """DOCSTRING PENDING"""

        # Get configration on run
        language_code: str = AppConfig.GoogleTTSConfig.language_code
        ssml_gender = AppConfig.GoogleTTSConfig.ssml_gender
        voice_name: str = AppConfig.GoogleTTSConfig.voice_name
        audio_encoding = AppConfig.GoogleTTSConfig.audio_encoding
        speaking_rate: float = AppConfig.GoogleTTSConfig.speaking_rate
        pitch: float = AppConfig.GoogleTTSConfig.pitch
        volume_gain_db: float = AppConfig.GoogleTTSConfig.volume_gain_db

        tts_client = texttospeech.TextToSpeechClient(
            client_options={"api_key": api_keys.google_cloud_api_key, "quota_project_id": api_keys.google_project_id}
        )
        input_for_synthesis = texttospeech.SynthesisInput({"text": f"{line}"})
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
        logger.info(f'TTS_API_CALL: Line {index} of {total_count}: {line}')

        api_response = tts_client.synthesize_speech(
            input=input_for_synthesis,
            voice=voice_settings,
            audio_config=audio_configuration)

        logger.info(f'TTS_API_CALL for {line} was sucessful')

        return (line, api_response.audio_content)

    @staticmethod
    def preprocess_with_kairyou(input_string: str, input_replacements_dict: dict):
        preprocessor = Kairyou(text_to_preprocess=input_string, replacements_json=input_replacements_dict)
        preprocessor.preprocess()
        output = preprocessor.text_to_preprocess
        return output

    @staticmethod
    def post_process_dialogue(input_string:str, *args):
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
