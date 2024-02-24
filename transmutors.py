## built-in libraries
import typing
import asyncio
import inspect

## third-party libraries
import backoff

from loguru import logger

from pyppeteer import launch as PyppeteerLaunch
from pyppeteer.errors import TimeoutError, PageError, NetworkError, BrowserError

from deepl.translator import Translator as DeepLTranslator
from deepl.api_data import TextResult
from deepl import exceptions as DeepLExceptions

from google.cloud import texttospeech as GCloudTTS
from google.cloud.texttospeech import TextToSpeechClient as GCloudTTSClient
from google.cloud.translate_v2 import Client as GCloudTranslateV2
from google.cloud.translate_v3 import TranslationServiceClient as GCloudTranslateV3
from google.api_core import exceptions as GCloudExceptions

from openai import AsyncOpenAI

from kairyou import Kairyou

## custom modules
from appconfig import AppConfig, FukuinConfig
from custom_modules import custom_exceptions
from custom_modules import utilities
from custom_modules.utilities import MetaLogger
from custom_modules.custom_exceptions import WebPageLoadError
from db_management import JishoParseDBM, DeepLDBM, TextToSpeechDBM, GoogleTLDBM
from nlp_modules.kroatoanjp_fukuin.preprocess import preprocessor as Fukuin
from nlp_modules.kroatoanjp_fukuin.preprocess.tokenizer.spacy_tokenizer import SpacyTokenizer


def log_backoff_retry(details):
    MetaLogger.log_backoff_retry(details)


def log_backoff_giveup(details):
    MetaLogger.log_backoff_giveup(details)


def log_backoff_success(details):
    MetaLogger.log_backoff_success(details)


def get_deepl_api_key() -> str:
    with open(AppConfig.deepl_api_key_path, 'r') as file:
        api_key = file.read().strip()

    return api_key


def get_openai_api_key() -> str:
    with open(AppConfig.openai_api_key_path, 'r') as file:
        api_key = file.read().strip()

    return api_key

class Initialize:
    @staticmethod
    def api_clients() -> tuple[
        typing.Union[GCloudTTSClient, None], typing.Union[GCloudTranslateV2, None], typing.Union[
            GCloudTranslateV3, None], typing.Union[DeepLTranslator, None], typing.Union[AsyncOpenAI, None]]:
        try:

            tts_client = GCloudTTS.TextToSpeechClient()

        except Exception as e:
            logger.warning(f'Skipping Google Text-to-Speech API client creation: {e}')
            tts_client = None

        try:
            gtl2_client = GCloudTranslateV2()  ## v2 of the API
            gtl3_client = GCloudTranslateV3()  ## v3 of the API

        except Exception as e:
            logger.warning(f'Skipping Google Cloud Translate API client creation: {e}')
            gtl2_client = None
            gtl3_client = None

        try:

            deepl_client = DeepLTranslator(auth_key=get_deepl_api_key())

        except Exception as e:
            logger.warning(f'Skipping DeepL API client creation: {e}')
            deepl_client = None

        try:

            openai_client = AsyncOpenAI(api_key=get_openai_api_key(), max_retries=0)

        except Exception as e:
            logger.warning(f'Skipping OpenAI API client creation: {e}')
            openai_client = None

        return tts_client, gtl2_client, gtl3_client, deepl_client, openai_client

    @staticmethod
    def fukuin_tokenizer() -> SpacyTokenizer:

        try:
            tokenizer = SpacyTokenizer(user_dic_path=FukuinConfig.user_dic_path)
        except Exception as e:
            logger.warning(f'Spacy tokenzier for Fukuin could not be initialized: {e}')
            raise e  # Needs better handling

        return tokenizer



class APIRequest:

    @staticmethod
    @backoff.on_exception(
        backoff.expo,
        exception=(DeepLExceptions.DeepLException, DeepLExceptions.TooManyRequestsException),
        max_tries=AppConfig.backoff_max_tries,
        max_time=AppConfig.backoff_max_time,
        on_backoff=log_backoff_retry,
        on_giveup=log_backoff_giveup,
        on_success=log_backoff_success)
    def deepl(
            text: typing.Union[str, list[str]],
            source_lang: str,
            target_lang: str,
            api_client: typing.Union[DeepLTranslator, None] = None) -> typing.Union[TextResult, list[TextResult]]:
        """
        Returns a TextResult object as defined by the deepl python client
        TextResult.text = <<Translated Text>>
        TextResult.detectedSourceLang
        """

        # if an API client was not provided, instantiate one
        if not api_client:
            try:
                api_client = DeepLTranslator(auth_key=get_deepl_api_key())
            except Exception as e:
                # TO DO
                raise e

        try:
            response = api_client.translate_text(
                text=text,  # The client can accept a singular string, or a list of stings
                source_lang=source_lang,
                target_lang=target_lang)

        except DeepLExceptions.QuotaExceededException as e:
            logger.critical('DeepL API request failed due to your quota being exceeded.')
            raise e
        except DeepLExceptions.TooManyRequestsException as e:
            raise e
        except DeepLExceptions.DeepLException as e:
            raise e
        except Exception as e:
            logger.critical(f'Deepl API request failed due to an unexpected error')
            raise e

        return response

    @staticmethod
    @backoff.on_exception(
        backoff.expo,
        exception=(
                GCloudExceptions.BadGateway,
                GCloudExceptions.DataLoss,
                GCloudExceptions.DeadlineExceeded,
                GCloudExceptions.GatewayTimeout,
                GCloudExceptions.GoogleAPICallError,
                GCloudExceptions.GoogleAPIError,
                GCloudExceptions.ServerError,
                GCloudExceptions.ServiceUnavailable,
                GCloudExceptions.TooManyRequests),
        # Google APIs do implement exponential backoff-retry for 5xx errors within it's client libraries.
        max_tries=AppConfig.backoff_max_tries,
        max_time=AppConfig.backoff_max_time,
        on_backoff=log_backoff_retry,
        on_giveup=log_backoff_giveup,
        on_success=log_backoff_success)
    def google_translate_v2(
            text: typing.Union[str, list[str]],
            source_lang: str,
            target_lang: str,
            api_client: typing.Union[GCloudTranslateV2, None] = None) -> list[dict]:
        """
        Returns: A list of dictionaries for each queried value. Each
                  dictionary typically contains three keys (though not
                  all will be present in all cases)

                  "detectedSourceLanguage": The detected language (as an
                    ISO 639-1 language code) of the text.
                  "translatedText": The translation of the text into the
                    target language.
                  "input": The corresponding input value.
                  "model": The model used to translate the text.

                  If only a single value is passed, then only a single
                  dictionary will be returned.
        """
        # if an API client was not provided, instantiate one
        if not api_client:
            try:
                api_client = GCloudTranslateV2()
            except Exception as e:
                # TO DO
                raise e

        try:
            response = api_client.translate(
                values=text,  # The client can accept a singular string, or a list of stings
                source_language=source_lang,
                target_language=target_lang,
                format_='text',
                model='nmt')
        except Exception as e:
            MetaLogger.log_exception(function='parse_string_with_jisho', exception=e)
            raise e

        return response


class Transmute:
    tts_client, gtl2_client, gtl3_client, deepl_client, openai_client = Initialize.api_clients()
    fukuin_tokenizer = Initialize.fukuin_tokenizer()

    # Jisho web scrape and parse
    @staticmethod
    async def parse_string_with_jisho(
            input_string: str,
            timestamp: int,
            progress_monitor: utilities.ProgressMonitor,
            semaphore: asyncio.Semaphore,
            index: int = 0,
            total_count: int = 0,
            browser: PyppeteerLaunch = None) -> tuple[str, str]:

        """DOCSTRING PENDING"""

        @backoff.on_exception(
            backoff.expo,
            exception=(WebPageLoadError),
            max_tries=AppConfig.backoff_max_tries,
            max_time=AppConfig.backoff_max_time,
            on_backoff=log_backoff_retry)
        async def get_element_outer_html(_url: str, _selector: str, _semaphore: asyncio.Semaphore,
                                         _browser: PyppeteerLaunch = None):
            async with _semaphore:
                if not _browser:
                    try:
                        _browser = await PyppeteerLaunch(

                            handleSIGINT=False,
                            handleSIGTERM=False,
                            handleSIGHUP=False)
                        browser_launched_within_function = True
                        logger.warning(
                            'Browser was not provided. A new browser instance will be run for each iteration. '
                            'This will add considerable overhead.')
                    except BrowserError as e:
                        raise e
                else:
                    browser_launched_within_function = False

                page = await _browser.newPage()

                try:
                    await page.goto(_url)
                    # Check if the webpage has actually loaded by locating the search bar
                    _ = await page.querySelector('#search_main')
                except (NetworkError, TimeoutError, PageError) as e:
                    logger.error(f'There was an error while loading the page for {_url}')
                    raise WebPageLoadError()

                if AppConfig.deep_log_transmutors:
                    logger.info(f'Webpage loaded for {index}: {_url}')

                element = await page.querySelector(_selector)

                if element:
                    outer_html = await page.evaluate('(element) => element.outerHTML', element)
                    if browser_launched_within_function:
                        await _browser.close()
                    return outer_html
                else:
                    if browser_launched_within_function:
                        await _browser.close()
                    raise PageError

        if AppConfig.MANUAL_RUN_STOP or AppConfig.GLOBAL_RUN_STOP:
            return  # type: ignore

        jisho_parsed_html_element = str()

        url = f'https://jisho.org/search/{input_string}'
        selector = f'#zen_bar'

        try:
            outer_html = await get_element_outer_html(url, selector, _semaphore=semaphore, _browser=browser)
            if outer_html:
                zen_outer_html = outer_html
                # replace linebreaks that mess with the html when assigned to a string_list
                zen_html = str(zen_outer_html).replace('\n', "").strip()
                jisho_parsed_html_element += zen_html
        except PageError as e:
            logger.error(f'A page error occurred in jisho parse - {input_string} '
                         f'Probable cause: The sentence parse HTML element was not found on page'
                         f'\n Reason: Line may not have a valid sentence parsing. Eg: Single words')
            zen_html = f'<p></p>'
            jisho_parsed_html_element += zen_html
        except Exception as e:
            logger.critical(
                f'A CRITICAL exception occurred in jisho parse - {input_string} \n Exception: {e} \n PARSE FAILED')
            AppConfig.GLOBAL_RUN_STOP = True
            logger.warning(f'CRITICAL ERROR: GLOBAL RUN STOP FLAG SET')
            return (input_string, "failed")

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
    def translate_with_deepl_api(
            input_data: typing.Union[str, list[str]],
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
            logger.info(f'CALLING_DEEPL_API: Chunk {index} of {total_count}: {input_data}')

        response = APIRequest.deepl(
            text=input_data,
            source_lang=source_lang,
            target_lang=target_lang,
            api_client=Transmute.deepl_client)

        ## If the response is a single TextResult, convert it to a list
        if isinstance(response, TextResult):
            response = [response]

        db_interface = DeepLDBM()

        for input_text, result in zip(input_data, response):
            translated_text = result.text
            db_interface.insert(raw_line=input_text, transmuted_data=translated_text, unix_timestamp=timestamp)
        db_interface.close_connection()

        progress_monitor.mark_completion()

        _ = "success"

        return (str(index), _)

    # Google Cloud Translate API
    @staticmethod
    def translate_with_google_tl_api(
            input_data: typing.Union[str, list[str]],
            timestamp: int,
            progress_monitor: utilities.ProgressMonitor,
            index: int = 0,
            total_count: int = 0) -> tuple[str, str]:

        """DOCSTRING PENDING"""

        if Transmute.gtl2_client is None:
            raise custom_exceptions.TransmuterNotAvailable("Google Translate API client is not available.")

        if AppConfig.MANUAL_RUN_STOP or AppConfig.GLOBAL_RUN_STOP:
            return  # type: ignore

        source_lang = AppConfig.GoogleTranslateConfig.source_language_code
        target_lang = AppConfig.GoogleTranslateConfig.target_language_code

        if AppConfig.deep_log_transmutors:
            logger.info(f'CALLING_GCLOUD_Translate_API: Chunk {index} of {total_count}: {input_data}')

        response = APIRequest.google_translate_v2(
            text=input_data,
            source_lang=source_lang,
            target_lang=target_lang,
            api_client=Transmute.gtl2_client)

        db_interface = GoogleTLDBM()
        for result in response:
            input_text = result['input']
            translated_text = result['translatedText']
            db_interface.insert(raw_line=input_text, transmuted_data=translated_text, unix_timestamp=timestamp)
        db_interface.close_connection()

        progress_monitor.mark_completion()

        _ = "success"

        return (str(index), _)

    # Google Cloud Text-to-Speech
    @staticmethod
    def tts_string_with_google_api(
            input_string: str,
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

        input_for_synthesis = GCloudTTS.SynthesisInput({"text": f"{input_string}"})
        voice_settings = GCloudTTS.VoiceSelectionParams(
            {
                "language_code": language_code,
                "name": voice_name
            }
        )
        audio_configuration = GCloudTTS.AudioConfig(
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
    def preprocess_with_fukuin(text: typing.Union[str, list], path_to_replacements_table: str) -> str:
        preprocessed_text = Fukuin.run_nlp_mtl_preprocessor(
            input_string=text,
            path_to_replacements_table=path_to_replacements_table,
            verbose=False
        )
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
