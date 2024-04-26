## built-in libraries
import json
import os.path
import time
import asyncio
import gzip
import argparse

## third-party libraries
from loguru import logger

## custom modules
from appconfig import AppConfig, RunConfig
from custom_dataclasses import RekaiText
from generators import GenerateRekaiPortable
from custom_modules.utilities import get_current_timestamps
from cf_db_worker import put_db_insert
from git_python_experiment import git_commit_all, git_push


def generate_and_push_to_cloud(
        japanese_text, preprocessed_text, chapter_id, chapter_uid, chapter_title, narou_link):

    start_time = time.time()
    timestamp_str, timestamp_unix = get_current_timestamps()
    log_path = os.path.join(AppConfig.logging_directory, f'rekai_push_log_{timestamp_str}_{chapter_id}.log')
    logger.add(sink=log_path, enqueue=True)

    # Reset previously rased flags
    AppConfig.MANUAL_RUN_STOP = False
    AppConfig.GLOBAL_RUN_STOP = False
    AppConfig.TRANSMUTE_FAILURE = False

    run_config = RunConfig(timestamp_unix)

    rekai_text_object = RekaiText(
        input_text=japanese_text,
        input_preprocessed_text=preprocessed_text,
        run_config_object=run_config,
        text_header=chapter_id)

    logger.info('Fetching data into RekaiText')
    asyncio.run(rekai_text_object.fetch_data())
    logger.success('FETCH COMPLETE')

    if not AppConfig.MANUAL_RUN_STOP:
        logger.info("Generating RekaiText JSON")
        rekai_text_json, rekai_text_tts_json = GenerateRekaiPortable.rekai_json(
            input_rekai_text_object=rekai_text_object)
    else:
        return

    repository_path = "C:\\Users\\prav9\\OneDrive\\Desktop\\Coding\\MTL\\rekai-datastore"
    output_save_path = f'{repository_path}\\{chapter_id}.json.gz'
    branch_name = "main"
    commit_message = "Committing new files"

    with gzip.open(output_save_path, 'wb') as gzip_file:
        gzip_file.write(rekai_text_json.encode('utf-8'))

    logger.info('Rekai JSON saved')

    # Commit all changes
    git_commit_all(repository_path, commit_message)
    git_push(repository_path, branch_name)

    index_entry_dict = {
        "chapter_uid": chapter_uid,
        "chapter_id": chapter_id,
        "chapter_title": chapter_title,
        "narou_link": narou_link,
        "rekai_text_json_link": f"https://rekai-datastore.pages.dev/{chapter_id}.json.gz",
        "upload_timestamp": timestamp_unix
    }

    rekai_index_dbm_url = 'https://rekai-db-manager.toshiroakari.workers.dev/dbinsert'
    index_entry_json = json.dumps(index_entry_dict)
    asyncio.run(put_db_insert(worker_url=rekai_index_dbm_url, index_json_string=index_entry_json))

    end_time = time.time()
    logger.success(f'Function complete. Time taken: {end_time - start_time}')

    return True


def main():
    parser = argparse.ArgumentParser(description='Rekai Transmute')
    parser.add_argument('japanese_text', type=str, help='Japanese RAW text to be processed')
    parser.add_argument('preprocessed_text', type=str, help='Preprocessed text to be processed')
    parser.add_argument('chapter_id', type=str, help='Chapter ID')
    parser.add_argument('chapter_uid', type=str, help='Chapter UID')
    parser.add_argument('chapter_title', type=str, help='Chapter UID')
    parser.add_argument('narou_link', type=str, help='Chapter UID')

    args = parser.parse_args()

    japanese_text = args.japanese_text
    preprocessed_text = args.preprocessed_text
    chapter_id = args.chapter_id
    chapter_uid = args.chapter_uid
    chapter_title = args.chapter_title
    narou_link = args.narou_link

    result = generate_and_push_to_cloud(
        japanese_text=japanese_text,
        preprocessed_text=preprocessed_text,
        chapter_id=chapter_id,
        chapter_uid=chapter_uid,
        chapter_title=chapter_title,
        narou_link=narou_link)

    return result


if __name__ == "__main__":
    main()
