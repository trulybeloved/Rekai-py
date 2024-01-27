# -*- coding: utf-8 -*-

"""
@author: beloved

This app will take japanese text as input, carry out all the NLP tasks, and save everything in a structured database
along with media files in proper folders

Features:
- gradio UI for interfacing
- Incorporate Kudasai Preprocessor
-

Todo

- Add check for internet connectivity
- add assertion error try accept blocks to data processing pipelines
- improve unparsability check
- add paragraph classifier
"""
import os.path
import time

import gradio as gr
from loguru import logger

from appconfig import AppConfig, RunConfig
from custom_dataclasses import RekaiText
from processors import Process
from generators import GenerateHtml
from custom_modules.utilities import get_current_timestamps
from custom_modules.utilities import log_process_time
# ----------------------------------------------------------------------------------------------------------------------#
# GLOBAL VARIABLES
# ----------------------------------------------------------------------------------------------------------------------#


# ----------------------------------------------------------------------------------------------------------------------#
# GRADIO WEBGUI
# ----------------------------------------------------------------------------------------------------------------------#


# Test Function
def rekai_test(japanese_text, preprocessed_text, header):

    start_time = time.time()

    timestamp_str, timestamp_unix = get_current_timestamps()

    output_directory = AppConfig.output_directory

    run_config = RunConfig(timestamp_unix)

    final_output_path = os.path.join(output_directory, f'Rekai_HTML_{timestamp_str}')

    rekai_text_object = RekaiText(input_text=japanese_text, input_preprocessed_text=preprocessed_text, run_config_object=run_config, text_header=header)

    if AppConfig.GLOBAL_RUN_STOP:
        logger.critical(f'GLOBAL STOP FLAG RAISED. FUNCTION TERMINATED')
        return

    if run_config.run_jisho_parse:
        jisho_start_time = time.time()
        Process.jisho_parse(rekai_text_object=rekai_text_object)
        jisho_end_time = time.time()
        logger.success(f'Function complete. Time taken: {jisho_end_time - jisho_start_time}')

    if run_config.run_tts:
        tts_start_time = time.time()
        Process.gcloud_tts(rekai_text_object=rekai_text_object)
        tts_end_time = time.time()
        logger.success(f'Function complete. Time taken: {tts_end_time - tts_start_time}')

    if run_config.run_deepl_tl:
        deepl_start_time = time.time()
        Process.deepl_tl(rekai_text_object=rekai_text_object)
        deepl_end_time = time.time()
        logger.success(f'Function complete. Time taken: {deepl_end_time - deepl_start_time}')

    if run_config.run_google_tl:
        gtl_start_time = time.time()
        Process.google_tl(rekai_text_object=rekai_text_object)
        gtl_end_time = time.time()
        logger.success(f'Function complete. Time taken: {gtl_end_time - gtl_start_time}')

    GenerateHtml.RekaiHtml.full_html(run_config_object=run_config, input_rekai_text_object=rekai_text_object,
                                     html_title='Rekai_Test', output_directory=final_output_path, post_process='minify', single_file_mode=False)

    if run_config.output_single_file:
        GenerateHtml.RekaiHtml.full_html(run_config_object=run_config, input_rekai_text_object=rekai_text_object,
                                         html_title='Rekai_Test', output_directory=final_output_path, post_process=None,
                                         single_file_mode=True)
    end_time = time.time()

    logger.success(f'Function complete. Time taken: {end_time - start_time}')

# Frontend

if __name__ == '__main__':

    CustomTest.rekai_test()