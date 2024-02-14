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
import random
import time
import asyncio

import gradio as gr
from loguru import logger

from appconfig import AppConfig, RunConfig
from custom_dataclasses import RekaiText
from processors import Process
from generators import GenerateHtml
from custom_modules.utilities import get_current_timestamps
from custom_modules.utilities import log_execution_time, ProgressMonitor
# ----------------------------------------------------------------------------------------------------------------------#
# GLOBAL VARIABLES
# ----------------------------------------------------------------------------------------------------------------------#


# ----------------------------------------------------------------------------------------------------------------------#
# GRADIO WEBGUI
# ----------------------------------------------------------------------------------------------------------------------#


# Main Function
def main(japanese_text, preprocessed_text, header):

    start_time = time.time()
    ProgressMonitor.destroy_all_instances()
    main_progress_monitor = ProgressMonitor(task_name='Overall', total_task_count=10)
    timestamp_str, timestamp_unix = get_current_timestamps()
    log_path = os.path.join(AppConfig.logging_directory, f'rekai_log_{timestamp_str}_{header}.log')
    logger.add(sink=log_path, enqueue=True)

    output_directory = AppConfig.output_directory

    run_config = RunConfig(timestamp_unix)

    final_output_path = os.path.join(output_directory, f'Rekai_HTML_{timestamp_str}_{header}')

    rekai_text_object = RekaiText(
        input_text=japanese_text,
        input_preprocessed_text=preprocessed_text,
        run_config_object=run_config,
        text_header=header)

    main_progress_monitor.mark_completion(1)

    if AppConfig.GLOBAL_RUN_STOP:
        logger.critical(f'GLOBAL STOP FLAG RAISED. FUNCTION TERMINATED')
        return

    async def run_jisho_parse(rekai_text_object):
        jisho_start_time = time.time()
        _ = await Process.jisho_parse(rekai_text_object=rekai_text_object)
        jisho_end_time = time.time()
        if not AppConfig.MANUAL_RUN_STOP:
            logger.success(f'Jisho Parse - Function complete. Time taken: {jisho_end_time - jisho_start_time}')
        main_progress_monitor.mark_completion(2)

    async def run_gcloud_tts(rekai_text_object):
        tts_start_time = time.time()
        _ = await Process.gcloud_tts(rekai_text_object=rekai_text_object)
        tts_end_time = time.time()
        if not AppConfig.MANUAL_RUN_STOP:
            logger.success(f'TTS - Function complete. Time taken: {tts_end_time - tts_start_time}')
        main_progress_monitor.mark_completion(2)

    async def run_deepl_tl(rekai_text_object):
        deepl_start_time = time.time()
        _ = await Process.deepl_tl(rekai_text_object=rekai_text_object)
        deepl_end_time = time.time()
        if not AppConfig.MANUAL_RUN_STOP:
            logger.success(f'Deepl TL - Function complete. Time taken: {deepl_end_time - deepl_start_time}')
        main_progress_monitor.mark_completion(2)

    async def run_google_tl(rekai_text_object):
        jisho_start_time = time.time()
        _ = await Process.google_tl(rekai_text_object=rekai_text_object)
        jisho_end_time = time.time()
        if not AppConfig.MANUAL_RUN_STOP:
            logger.success(f'Google TL - Function complete. Time taken: {jisho_end_time - jisho_start_time}')
        main_progress_monitor.mark_completion(2)

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
        asyncio.run(async_transmute())
    else:
        logger.critical(f'MANUAL STOP FLAG RAISED. FUNCTION TERMINATED')
        return

    if not AppConfig.MANUAL_RUN_STOP:
        zip_file_path = GenerateHtml.RekaiHtml.full_html(
            run_config_object=run_config,
            input_rekai_text_object=rekai_text_object,
            html_title=header,
            output_directory=final_output_path,
            post_process='minify',
            single_file_mode=False)

        if run_config.output_single_file:
            GenerateHtml.RekaiHtml.full_html(
                run_config_object=run_config,
                input_rekai_text_object=rekai_text_object,
                html_title=header,
                output_directory=final_output_path,
                post_process=None,
                single_file_mode=True)
    else:
        logger.critical(f'MANUAL STOP FLAG RAISED. FUNCTION TERMINATED')
        return

    end_time = time.time()

    logger.success(f'Function complete. Time taken: {end_time - start_time}')

    main_progress_monitor.mark_completion(1)

    return zip_file_path

# Associated Functions

def progress_monitor():
    progress_df = ProgressMonitor.get_progress_dataframe()
    return progress_df

def set_manual_stop_flag():
    AppConfig.MANUAL_RUN_STOP = True
    logger.critical('MANUAL STOP FLAG SET')

# Frontend
with gr.Blocks() as rekai_webgui:
    gr.Markdown("""# Re:KAI""")

    with gr.Tab('RekaiHTML') as rekai_html_tab:

        with gr.Row():

            with gr.Column():

                gr.Markdown('## Inputs')

                html_header_input_textbox = gr.Textbox(
                    label='Header',
                    lines=1,
                    max_lines=2,
                    visible=True,
                    interactive=True)

                clear_button_header = gr.ClearButton(components=[html_header_input_textbox], size='sm')

                raw_input_text_box = gr.Textbox(
                    label='Japanese Raw Text',
                    value='',
                    lines=10,
                    max_lines=10,
                    visible=True,
                    interactive=True,
                    placeholder='Input Japanese Raw text here')

                clear_button_raw = gr.ClearButton(components=[raw_input_text_box], size='sm')

                preprocessed_input_text_box = gr.Textbox(
                    label='Preprocessed Text',
                    value='',
                    lines=10,
                    max_lines=10,
                    visible=True,
                    interactive=True,
                    placeholder='Input Preprocessed text here')

                clear_button_prepro = gr.ClearButton(components=[preprocessed_input_text_box], size='sm')

                clear_button_all = gr.ClearButton(
                    components=[html_header_input_textbox, raw_input_text_box, preprocessed_input_text_box],
                    size='lg',
                    value='Clear All')

                html_generate_button = gr.Button(
                    value='Generate HTML',
                    variant='primary',
                    interactive=True,
                    visible=True)

                html_interrupt_button = gr.Button(
                    value='Stop',
                    variant='stop',
                    interactive=True,
                    visible=True)

                with gr.Accordion(label='Options', open=False):

                    with gr.Column():
                        gr.Markdown('#### Processing Options')
                        gr.Markdown('''These toggles control which processes to run on your input text. 
                        Unchecking them will also mean that they will not be rendered in the final output, 
                        regardless of the output options below''')

                        run_options_jishoparse = gr.Checkbox(
                            value=True,
                            label='JishoParse',
                            info='Perform sentence parsing using Jisho',
                            container=True,
                            interactive=True)

                        run_options_tts = gr.Checkbox(
                            value=True,
                            label='Text-to-Speech',
                            info='Enable Text-to-Speech',
                            container=True,
                            interactive=True)

                        run_options_preprocess = gr.Checkbox(
                            value=True,
                            label='Preprocess',
                            info='Use preprocessed text for translation',
                            container=True,
                            interactive=True)

                        run_options_deepl_tl = gr.Checkbox(
                            value=True,
                            label='DeepL TL',
                            info='Translate using DeepL',
                            container=True,
                            interactive=True)

                        run_options_google_tl = gr.Checkbox(
                            value=True,
                            label='Google TL',
                            info='Translate using Google',
                            container=True,
                            interactive=True)

                        run_options_clean_post_split = gr.Checkbox(
                            value=True,
                            label='Clean Clauses',
                            info='Remove trailing punctuation marks when sentences are split into clauses',
                            container=True,
                            interactive=True)

                    with gr.Column():
                        gr.Markdown('#### Processing Levels')
                        with gr.Group():

                            text_options_deepl = gr.CheckboxGroup(
                                choices=[('Para', 'para'), ('Lines', 'line'), ('Clauses', 'clauses')],
                                label='DeepL Translate:',
                                value=['line', 'clauses'],
                                interactive=True)

                            text_options_use_prepro_deepl = gr.Checkbox(
                                value=True, label='Use Preprocessed for Deepl TL',
                                container=True,
                                interactive=True)

                        with gr.Group():

                            text_options_google_tl = gr.CheckboxGroup(
                                choices=[('Para','para'), ('Lines', 'line'), ('Clauses', 'clauses')],
                                label='Google Translate:',
                                value=['line', 'clauses'],
                                interactive=True)

                            text_options_use_prepro_google_tl = gr.Checkbox(
                                value=True,
                                label='Use Preprocessed for Google TL',
                                container=True,
                                interactive=True)


                    with gr.Column():
                        gr.Markdown('#### Output Options')
                        with gr.Group():

                            output_options_include_jisho_parse = gr.Checkbox(
                                value=True,
                                label='Jisho Parse',
                                container=True,
                                interactive=True)

                            output_options_include_clause_analysis = gr.Checkbox(
                                value=True,
                                label='Clause Analysis',
                                container=True,
                                interactive=True)

                        with gr.Group():

                            output_options_also_output_single_file = gr.Checkbox(
                                value=False,
                                label='Output Single File version',
                                info='Generate a single self contained HTML in addition to regular output',
                                interactive=True  )

                        # output_options_include_clause_analysis = gr.Checkbox(value=True, label='Clause Analysis', container=True, interactive=True)
                        # output_options_include_clause_analysis = gr.Checkbox(value=True, label='Clause Analysis', container=True, interactive=True)
                        # output_options_include_clause_analysis = gr.Checkbox(value=True, label='Clause Analysis', container=True, interactive=True)


            with gr.Column():

                gr.Markdown('## Output')

                output_rekai_html_file = gr.File(
                    value=None,
                    file_count="single",
                    type="filepath",
                    label="Output Zip File",
                    container=True
                )

                transmutors_progress_barplot = gr.BarPlot(
                    value=ProgressMonitor.get_progress_dataframe(),
                    vertical=False,
                    title="Transmutation Progress",
                    x="Transmutor",
                    y="Progress",
                    color="Transmutor",
                    y_lim=[0, 100],
                    container=False,
                    width=500,
                    height=400,
                    interactive=False)

                rekai_html_log_area = gr.Textbox(
                    label='Log',
                    value='',
                    lines=10,
                    max_lines=20,
                    visible=True,
                    interactive=False)

    with gr.Tab("Settings") as preprocess_tab:
        with gr.Column():
            pass


    ## Event Listeners
    run_main = html_generate_button.click(
        fn=main,
        inputs=[raw_input_text_box, preprocessed_input_text_box, html_header_input_textbox],
        outputs=[output_rekai_html_file])

    progress_monitoring = html_generate_button.click(
        fn=progress_monitor,
        inputs=[],
        outputs=[transmutors_progress_barplot],
        every=1)

    html_interrupt_button.click(fn=set_manual_stop_flag, inputs=[], outputs=[], cancels=[run_main, progress_monitoring])

    output_rekai_html_file.change(fn=None, inputs=None, outputs=None, cancels=progress_monitoring)


if __name__ == '__main__':

    rekai_webgui.queue().launch(inbrowser=True)