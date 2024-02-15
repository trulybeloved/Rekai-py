## built-in-libraries
import asyncio

## third-party libraries
import backoff

from loguru import logger

from pyppeteer import launch as PyppeteerLaunch
from pyppeteer.errors import TimeoutError, PageError, NetworkError, BrowserError

from google.cloud import texttospeech
from google.cloud import translate
from google.cloud import translate_v2 as translatev2

from openai import AsyncOpenAI
from kairyou import Kairyou

import deepl

## custom modules
from appconfig import AppConfig
from custom_modules import utilities
from custom_modules.custom_exceptions import WebPageLoadError
from db_management import JishoParseDBM, DeepLDBM, TextToSpeechDBM, GoogleTLDBM

import api_keys


class ApiKeyHandler:

    @staticmethod
    def get_deepl_api_key() -> str:
        return api_keys.deepl_api_key


class Transmute:

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

        @backoff.on_exception(backoff.expo, WebPageLoadError, max_tries=3, max_time=20)
        async def get_element_outer_html(_url: str, _selector: str, _semaphore: asyncio.Semaphore, _browser: PyppeteerLaunch = None):
            async with _semaphore:
                if not _browser:
                    try:
                        _browser = await PyppeteerLaunch(

                            handleSIGINT=False,
                            handleSIGTERM=False,
                            handleSIGHUP=False)
                        browser_launched_within_fucntion = True
                        logger.warning('Browser was not provided. A new browser instance will be run for each iteration. '
                                       'This will add considerable overhead.')
                    except BrowserError as e:
                        raise e
                else:
                    browser_launched_within_fucntion = False

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
                    if browser_launched_within_fucntion:
                        await _browser.close()
                    return outer_html
                else:
                    if browser_launched_within_fucntion:
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
            logger.critical(f'A CRITICAL exception occurred in jisho parse - {input_string} \n Exception: {e} \n PARSE FAILED')
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
    def translate_string_with_deepl_api(
            input_string: str,
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

        if AppConfig.deep_log_transmutors:
            logger.info(f'CALLING_DEEPL_API: Line {index} of {total_count}: {input_string}')

        response = translator.translate_text(text=input_string, source_lang=source_lang, target_lang="EN-US")

        result = response.text

        db_interface = DeepLDBM()
        db_interface.insert(raw_line=input_string, transmuted_data=result, unix_timestamp=timestamp)
        db_interface.close_connection()

        progress_monitor.mark_completion()

        _ = "success"

        return (input_string, _)

    @staticmethod
    def translate_chunk_with_deepl_api(
            input_chunk: list,
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

        if AppConfig.deep_log_transmutors:
            logger.info(f'CALLING_DEEPL_API: Chunk {index} of {total_count}: {input_chunk}')

        response = translator.translate_text(text=input_chunk, source_lang=source_lang, target_lang="EN-US")

        db_interface = DeepLDBM()
        for input_text, result in zip(input_chunk, response):
            translated_text = result.text
            db_interface.insert(raw_line=input_text, transmuted_data=translated_text, unix_timestamp=timestamp)
        db_interface.close_connection()

        progress_monitor.mark_completion()

        _ = "success"

        return (str(index), _)

    # Google Cloud Translate API
    @staticmethod
    def translate_string_with_google_tl_api(
            input_string: str,
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

        client = translate.TranslationServiceClient()  # This is v3 of the API

        if AppConfig.deep_log_transmutors:
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

        db_interface = GoogleTLDBM()
        db_interface.insert(raw_line=input_string, transmuted_data=result, unix_timestamp=timestamp)
        db_interface.close_connection()

        progress_monitor.mark_completion()

        _ = "success"

        return (input_string, _)

    @staticmethod
    def translate_chunk_with_google_tl_api(
            input_chunk: list,
            timestamp: int,
            progress_monitor: utilities.ProgressMonitor,
            index: int = 0,
            total_count: int = 0) -> tuple[str, str]:

        """DOCSTRING PENDING
        This API expects a list of strings.
        """


        if AppConfig.MANUAL_RUN_STOP or AppConfig.GLOBAL_RUN_STOP:
            return  # type: ignore

        source_lang = AppConfig.GoogleTranslateConfig.source_language_code
        target_lang = AppConfig.GoogleTranslateConfig.target_language_code
        location = AppConfig.GoogleTranslateConfig.location
        project_id = api_keys.google_project_id
        parent = f"projects/{project_id}/locations/{location}"  # not needed for v2

        client = translatev2.Client()  # NOT v3 but v2

        if AppConfig.deep_log_transmutors:
            logger.info(f'CALLING_GCLOUD_Translate_API: Chunk {index} of {total_count}: {input_chunk}')

        response = client.translate(
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

        if AppConfig.deep_log_transmutors:
            logger.info(f'CALLING_GCLOUD_TTS_API: Line {index} of {total_count}: {input_string}')

        response = tts_client.synthesize_speech(
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

        openai_client = AsyncOpenAI(api_key=api_keys.openai_api_key, max_retries=0)

        inference = await openai_client.chat.completions.create(
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
            output_string = "[" + input_string[1:]
        else:
            output_string = input_string

        if input_string[-1] in closing_characters:
            output_string = output_string[:-1] + "]"
        else:
            output_string = output_string

        return output_string
