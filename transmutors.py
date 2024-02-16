## built-in libraries
import typing

## third-party libraries
from loguru import logger

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from google.cloud import texttospeech
from google.cloud import translate
from google.cloud import translate_v2

from google.cloud.texttospeech import TextToSpeechClient
from google.cloud.translate_v2 import Client as translatev2
from google.cloud.translate_v3 import TranslationServiceClient

from openai import AsyncOpenAI

from kairyou import Kairyou

from deepl.translator import Translator
from deepl.api_data import TextResult

## custom modules
from appconfig import AppConfig
from custom_modules import utilities, custom_exceptions
from db_management import JishoParseDBM, DeepLDBM, TextToSpeechDBM, GoogleTLDBM

import api_keys


class ApiKeyHandler:

    @staticmethod
    def get_deepl_api_key() -> str:
        return api_keys.deepl_api_key
    

def create_transmutors() -> tuple[typing.Union[TextToSpeechClient, None], typing.Union[translatev2, None], typing.Union[TranslationServiceClient, None], typing.Union[Translator, None], typing.Union[AsyncOpenAI, None]]:
    try:

        tts_client = texttospeech.TextToSpeechClient(
                client_options={"api_key": api_keys.google_cloud_api_key, "quota_project_id": api_keys.google_project_id}
            )
        
    except Exception as e:
        logger.warning(f'Skipping Google Text-to-Speech API client creation: {e}')
        tts_client = None
    
    try:
        gtl2_client = translatev2() ## v2 of the API
        gtl3_client = translate.TranslationServiceClient()  ## v3 of the API

    except Exception as e:
        logger.warning(f'Skipping Google Cloud Translate API client creation: {e}')
        gtl2_client = None
        gtl3_client = None

    try:

        deepl_client = Translator(auth_key=ApiKeyHandler.get_deepl_api_key())

    except Exception as e:
        logger.warning(f'Skipping DeepL API client creation: {e}')
        deepl_client = None

    try:

        openai_client = AsyncOpenAI(api_key=api_keys.openai_api_key, max_retries=0)

    except Exception as e:
        logger.warning(f'Skipping OpenAI API client creation: {e}')
        openai_client = None

    return tts_client, gtl2_client, gtl3_client, deepl_client, openai_client



class Transmute:

    tts_client, gtl2_client, gtl3_client, deepl_client, openai_client = create_transmutors()

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
            if AppConfig.deep_log_transmutors:
                logger.info(f'Trying to parse line {index} out of {total_count}')

            driver.get(url=url)

            if AppConfig.deep_log_transmutors:
                logger.info(f'Webdriver instance Started for {index} started')

            zen_bar_element = WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.ID, "zen_bar")))
            zen_outer_html = zen_bar_element.get_attribute('outerHTML')

            # Selenium also extracts linebreaks that mess with the html when assigned to a string_list
            zen_html = str(zen_outer_html).replace('\n', "").strip()

            jisho_parsed_html_element += zen_html

        except Exception as e:
            logger.error(f'An exception occurred in jisho parse - {input_string}')
            zen_html = f'<p></p>'
            jisho_parsed_html_element += zen_html

        driver.quit()

        jisho_parsed_html_element = jisho_parsed_html_element.replace('/search/', 'https://jisho.org/search/')
        jisho_parsed_html_element = jisho_parsed_html_element.replace('class="current"', 'class=""')
        jisho_parsed_html_element = jisho_parsed_html_element.replace('class=""', 'class="jisho-link"')

        db_interface = JishoParseDBM()
        db_interface.insert(raw_line=input_string, transmuted_data=jisho_parsed_html_element, unix_timestamp=timestamp)
        db_interface.close_connection()

        progress_monitor.mark_completion()

        _ = "success"

        return (input_string, _)  # An explicit return only for asyncio to work properly.

    # DeepL API translation
    @staticmethod
    def translate_string_with_deepl_api(input_string: str,
                                        timestamp: int,
                                        progress_monitor: utilities.ProgressMonitor,
                                        index: int = 0,
                                        total_count: int = 0) -> tuple[str, str]:

        """DOCSTRING PENDING"""

        if Transmute.deepl_client is None:
            raise custom_exceptions.TransmuterNotAvailable("DeepL API client is not available.")

        if AppConfig.MANUAL_RUN_STOP or AppConfig.GLOBAL_RUN_STOP:
            return  # type: ignore

        source_lang = AppConfig.DeeplTranslateConfig.source_language_code
        target_lang = AppConfig.DeeplTranslateConfig.target_language_code

        if AppConfig.deep_log_transmutors:
            logger.info(f'CALLING_DEEPL_API: Line {index} of {total_count}: {input_string}')

        response:typing.Union[TextResult, typing.List[TextResult]] = Transmute.deepl_client.translate_text(text=input_string, source_lang=source_lang, target_lang=target_lang)

        if isinstance(response, list):
            result = [translation.text for translation in response]
            result = ''.join(result)
            
        else:
            result = response.text

        db_interface = DeepLDBM()
        db_interface.insert(raw_line=input_string, transmuted_data=result, unix_timestamp=timestamp)
        db_interface.close_connection()

        progress_monitor.mark_completion()

        _ = "success"

        return (input_string, _)

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

        if Transmute.gtl3_client is None:
            raise custom_exceptions.TransmuterNotAvailable("Google Translate API client is not available.")

        if AppConfig.MANUAL_RUN_STOP or AppConfig.GLOBAL_RUN_STOP:
            return  # type: ignore

        source_lang = AppConfig.GoogleTranslateConfig.source_language_code
        target_lang = AppConfig.GoogleTranslateConfig.target_language_code
        location = AppConfig.GoogleTranslateConfig.location
        project_id = api_keys.google_project_id
        parent = f"projects/{project_id}/locations/{location}"

        if AppConfig.deep_log_transmutors:
            logger.info(f'CALLING_GCLOUD_Translate_API: Line {index} of {total_count}: {input_string}')

        response = Transmute.gtl3_client.translate_text(
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

        db_interface = GoogleTLDBM()
        db_interface.insert(raw_line=input_string, transmuted_data=result, unix_timestamp=timestamp)
        db_interface.close_connection()

        progress_monitor.mark_completion()


        _ = "success"

        return (input_string, _)

    @staticmethod
    def translate_chunk_with_google_tl_api(input_chunk: list,
                                           timestamp: int,
                                           progress_monitor: utilities.ProgressMonitor,
                                           index: int = 0,
                                           total_count: int = 0) -> tuple[str, str]:

        """DOCSTRING PENDING
        This API expects a list of strings.
        """

        if Transmute.gtl2_client is None:
            raise custom_exceptions.TransmuterNotAvailable("Google Translate API client is not available.")

        if AppConfig.MANUAL_RUN_STOP or AppConfig.GLOBAL_RUN_STOP:
            return  # type: ignore

        source_lang = AppConfig.GoogleTranslateConfig.source_language_code
        target_lang = AppConfig.GoogleTranslateConfig.target_language_code
        location = AppConfig.GoogleTranslateConfig.location
        project_id = api_keys.google_project_id
        parent = f"projects/{project_id}/locations/{location}"  # not needed for v2

        if AppConfig.deep_log_transmutors:
            logger.info(f'CALLING_GCLOUD_Translate_API: Line {index} of {total_count}: {input_chunk}')

        response = Transmute.gtl2_client.translate(
            values=input_chunk,
            source_language=source_lang,
            target_language=target_lang,
            format_='text',
            model='nmt')

        db_interface = GoogleTLDBM()
        for result in response:
            input_text = result['input']
            translated_text = result['translatedText']
            db_interface.insert(raw_line=input_text, transmuted_data=translated_text, unix_timestamp=timestamp)
        db_interface.close_connection()

        progress_monitor.mark_completion()


        _ = "success"

        return (_, _)


    # Google Cloud Text-to-Speech
    @staticmethod
    def tts_string_with_google_api(input_string: str,
                                   timestamp: int,
                                   progress_monitor: utilities.ProgressMonitor,
                                   index: int = 0,
                                   total_count: int = 0) -> tuple[str, str]:

        """DOCSTRING PENDING"""

        if Transmute.tts_client is None:
            raise custom_exceptions.TransmuterNotAvailable("Google Text-to-Speech API client is not available.")

        if AppConfig.MANUAL_RUN_STOP or AppConfig.GLOBAL_RUN_STOP:
            return  # type: ignore

        # Get configuration on run
        language_code: str = AppConfig.GoogleTTSConfig.language_code
        voice_name: str = AppConfig.GoogleTTSConfig.voice_name
        audio_encoding = AppConfig.GoogleTTSConfig.audio_encoding
        speaking_rate: float = AppConfig.GoogleTTSConfig.speaking_rate
        pitch: float = AppConfig.GoogleTTSConfig.pitch
        volume_gain_db: float = AppConfig.GoogleTTSConfig.volume_gain_db

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

        if AppConfig.deep_log_transmutors:
            logger.info(f'CALLING_GCLOUD_TTS_API: Line {index} of {total_count}: {input_string}')

        response = Transmute.tts_client.synthesize_speech(
            input=input_for_synthesis,
            voice=voice_settings,
            audio_config=audio_configuration)

        result = utilities.encode_bytes_to_base64_string(response.audio_content)

        db_interface = TextToSpeechDBM()
        db_interface.insert(raw_line=input_string, transmuted_data=result, unix_timestamp=timestamp)
        db_interface.close_connection()

        progress_monitor.mark_completion()

        _ = "success"

        return (input_string, _)


    @staticmethod
    async def infer_openai_gpt(db_key_string: str, system_message: str, prompt: str):

        if Transmute.openai_client is None:
            raise custom_exceptions.TransmuterNotAvailable("OpenAI API client is not available.")

        inference = await Transmute.openai_client.chat.completions.create(
            model=AppConfig.OpenAIConfig.model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}],
            temperature=AppConfig.OpenAIConfig.temperature,
            top_p=AppConfig.OpenAIConfig.top_p,
            n=AppConfig.OpenAIConfig.n,
            stream=AppConfig.OpenAIConfig.stream
            )



    @staticmethod
    def preprocess_with_kairyou(input_string: str, input_replacements_dict: dict) -> str:
        preprocessed_text, _, _ = Kairyou.preprocess(input_string, input_replacements_dict)
        return preprocessed_text

    @staticmethod
    def post_process_dialogue(input_string: str, *args):
        """Replaces quotation/japanese quotation marks with []"""

        opening_characters = {"\"", "「"}
        closing_characters = {"\"", "」"}

        if input_string[0] in opening_characters:
            input_string = "[" + input_string[1:]

        if input_string[-1] in closing_characters:
            input_string = input_string[:-1] + "]"

        return input_string