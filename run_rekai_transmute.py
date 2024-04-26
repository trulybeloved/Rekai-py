## built-in libraries
import os.path
import time
import asyncio
import argparse

## third-party libraries
from loguru import logger

## custom modules
from appconfig import AppConfig, RunConfig
from custom_dataclasses import RekaiText
from processors import Process
from custom_modules.utilities import get_current_timestamps


# Main Function
def transmute(japanese_text, preprocessed_text, chapter_id):

    start_time = time.time()
    timestamp_str, timestamp_unix = get_current_timestamps()
    log_path = os.path.join(AppConfig.logging_directory, f'rekai_log_{timestamp_str}_{chapter_id}.log')
    logger.add(sink=log_path, enqueue=True)

    # Reset previously rased flags
    AppConfig.MANUAL_RUN_STOP = False
    AppConfig.GLOBAL_RUN_STOP = False
    AppConfig.TRANSMUTE_FAILURE = False

    ## get api keys working
    if not os.path.exists(AppConfig.deepl_api_key_path) or os.path.getsize(AppConfig.deepl_api_key_path) == 0:
        logger.warning(f'No DeepL API Key found. Prompting user to enter one')
        api_key = input('Enter your DeepL API Key: ')

        with open(AppConfig.deepl_api_key_path, 'w') as f:
            f.write(api_key)

    if not os.path.exists(AppConfig.openai_api_key_path) or os.path.getsize(AppConfig.openai_api_key_path) == 0:
        logger.warning(f'No OpenAI API Key found. Prompting user to enter one')
        api_key = input('Enter your OpenAI API Key: ')

        with open(AppConfig.openai_api_key_path, 'w') as f:
            f.write(api_key)

    run_config = RunConfig(timestamp_unix)

    rekai_text_object = RekaiText(
        input_text=japanese_text,
        input_preprocessed_text=preprocessed_text,
        run_config_object=run_config,
        text_header=chapter_id)

    if AppConfig.GLOBAL_RUN_STOP:
        logger.critical(f'GLOBAL STOP FLAG RAISED. FUNCTION TERMINATED')
        return

    async def run_jisho_parse(rekai_text_object):
        jisho_start_time = time.time()
        _ = await Process.jisho_parse(rekai_text_object=rekai_text_object)
        jisho_end_time = time.time()
        if not AppConfig.MANUAL_RUN_STOP:
            logger.success(f'Jisho Parse - Function complete. Time taken: {jisho_end_time - jisho_start_time}')

    async def run_gcloud_tts(rekai_text_object):
        tts_start_time = time.time()
        _ = await Process.gcloud_tts(rekai_text_object=rekai_text_object)
        tts_end_time = time.time()
        if not AppConfig.MANUAL_RUN_STOP:
            logger.success(f'TTS - Function complete. Time taken: {tts_end_time - tts_start_time}')

    async def run_deepl_tl(rekai_text_object):
        deepl_start_time = time.time()
        _ = await Process.deepl_tl(rekai_text_object=rekai_text_object)
        deepl_end_time = time.time()
        if not AppConfig.MANUAL_RUN_STOP:
            logger.success(f'Deepl TL - Function complete. Time taken: {deepl_end_time - deepl_start_time}')

    async def run_google_tl(rekai_text_object):
        jisho_start_time = time.time()
        _ = await Process.google_tl(rekai_text_object=rekai_text_object)
        jisho_end_time = time.time()
        if not AppConfig.MANUAL_RUN_STOP:
            logger.success(f'Google TL - Function complete. Time taken: {jisho_end_time - jisho_start_time}')

    async def async_transmute():
        tasks = []

        if run_config.run_jisho_parse:
            task_jisho = asyncio.create_task(run_jisho_parse(rekai_text_object))
            tasks.append(task_jisho)

        if run_config.run_tts:
            task_tts = asyncio.create_task(run_gcloud_tts(rekai_text_object))
            tasks.append(task_tts)

        if run_config.run_deepl_tl:
            task_deepl = asyncio.create_task(run_deepl_tl(rekai_text_object))
            tasks.append(task_deepl)

        if run_config.run_google_tl:
            task_google = asyncio.create_task(run_google_tl(rekai_text_object))
            tasks.append(task_google)

        # Wait for all tasks to complete
        await asyncio.gather(*tasks)

    if not AppConfig.MANUAL_RUN_STOP:
        # asyncio.run(async_transmute())
        logger.success('TRANSMUTORS CODE REACHED')
    else:
        logger.critical(f'MANUAL STOP FLAG RAISED. FUNCTION TERMINATED')
        return False

    end_time = time.time()

    logger.success(f'Function complete. Time taken: {end_time - start_time}')

    return True


def main():
    parser = argparse.ArgumentParser(description='Rekai Transmute')
    parser.add_argument('japanese_text', type=str, help='Japanese RAW text to be processed')
    parser.add_argument('preprocessed_text', type=str, help='Preprocessed text to be processed')
    parser.add_argument('chapter_id', type=str, help='Chapter ID')

    args = parser.parse_args()

    japanese_text = args.japanese_text
    preprocessed_text = args.preprocessed_text
    chapter_id = args.chapter_id

    result = transmute(japanese_text=japanese_text, preprocessed_text=preprocessed_text, chapter_id=chapter_id)

    return result


if __name__ == "__main__":
    main()
