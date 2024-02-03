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
import concurrent.futures

import gradio as gr
from loguru import logger

from appconfig import AppConfig, RunConfig
from custom_dataclasses import RekaiText
from processors import Process
from generators import GenerateHtml
from custom_modules.utilities import get_current_timestamps
from custom_modules.utilities import log_execution_time
# ----------------------------------------------------------------------------------------------------------------------#
# GLOBAL VARIABLES
# ----------------------------------------------------------------------------------------------------------------------#


# ----------------------------------------------------------------------------------------------------------------------#
# GRADIO WEBGUI
# ----------------------------------------------------------------------------------------------------------------------#


# Main Function
def main(japanese_text, preprocessed_text, header):

    start_time = time.time()

    # Reset cancellation flag if set previously
    AppConfig.MANUAL_RUN_STOP = False

    timestamp_str, timestamp_unix = get_current_timestamps()

    output_directory = AppConfig.output_directory

    run_config = RunConfig(timestamp_unix)

    final_output_path = os.path.join(output_directory, f'Rekai_HTML_{timestamp_str}_{header}')

    rekai_text_object = RekaiText(input_text=japanese_text, input_preprocessed_text=preprocessed_text, run_config_object=run_config, text_header=header)

    if AppConfig.GLOBAL_RUN_STOP:
        logger.critical(f'GLOBAL STOP FLAG RAISED. FUNCTION TERMINATED')
        return

    # if run_config.run_jisho_parse:
    #     jisho_start_time = time.time()
    #     Process.jisho_parse(rekai_text_object=rekai_text_object)
    #     jisho_end_time = time.time()
    #     logger.success(f'Function complete. Time taken: {jisho_end_time - jisho_start_time}')
    #
    # if run_config.run_tts:
    #     tts_start_time = time.time()
    #     Process.gcloud_tts(rekai_text_object=rekai_text_object)
    #     tts_end_time = time.time()
    #     logger.success(f'Function complete. Time taken: {tts_end_time - tts_start_time}')
    #
    # if run_config.run_deepl_tl:
    #     deepl_start_time = time.time()
    #     Process.deepl_tl(rekai_text_object=rekai_text_object)
    #     deepl_end_time = time.time()
    #     logger.success(f'Function complete. Time taken: {deepl_end_time - deepl_start_time}')
    #
    # if run_config.run_google_tl:
    #     gtl_start_time = time.time()
    #     Process.google_tl(rekai_text_object=rekai_text_object)
    #     gtl_end_time = time.time()
    #     logger.success(f'Function complete. Time taken: {gtl_end_time - gtl_start_time}')

    def run_jisho_parse(rekai_text_object):
        Process.jisho_parse(rekai_text_object=rekai_text_object)

    def run_gcloud_tts(rekai_text_object):
        Process.gcloud_tts(rekai_text_object=rekai_text_object)

    def run_deepl_tl(rekai_text_object):
        Process.deepl_tl(rekai_text_object=rekai_text_object)

    def run_google_tl(rekai_text_object):
        Process.google_tl(rekai_text_object=rekai_text_object)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        if run_config.run_jisho_parse:
            executor.submit(run_jisho_parse, rekai_text_object)

        if run_config.run_tts:
            executor.submit(run_gcloud_tts, rekai_text_object)

        if run_config.run_deepl_tl:
            executor.submit(run_deepl_tl, rekai_text_object)

        if run_config.run_google_tl:
            executor.submit(run_google_tl, rekai_text_object)

    GenerateHtml.RekaiHtml.full_html(run_config_object=run_config, input_rekai_text_object=rekai_text_object,
                                     html_title='Rekai_Test', output_directory=final_output_path, post_process='minify', single_file_mode=False)

    if run_config.output_single_file:
        GenerateHtml.RekaiHtml.full_html(run_config_object=run_config, input_rekai_text_object=rekai_text_object,
                                         html_title='Rekai_Test', output_directory=final_output_path, post_process=None,
                                         single_file_mode=True)
    end_time = time.time()

    logger.success(f'Function complete. Time taken: {end_time - start_time}')

def generate_run_config():
    pass

# Frontend
with gr.Blocks() as demo:
    gr.Markdown("""# Re:KAI""")

    with gr.Tab('RekaiHTML') as rekai_html_tab:

        # gr.Markdown('''### Generate RekaiHTML files for japanese text.''')

        with gr.Column():

            with gr.Column():

                gr.Markdown('## Inputs')

                html_header_input_textbox = gr.Textbox(label='Header', lines=1, max_lines=2, visible=True, interactive=True)

                raw_input_text_box = gr.Textbox(label='Japanese Raw Text', value='', lines=10, max_lines=20, visible=True, interactive=True,
                                                 placeholder='Input Japanese Raw text here')

                preprocessed_input_text_box = gr.Textbox(label='Preprocessed Text', value='', lines=10, max_lines=20,
                                                 visible=True, interactive=True,
                                                 placeholder='Input Preprocessed text here')

                html_generate_button = gr.Button(value='Generate HTML', variant='primary', interactive=True, visible=True)

                html_interrupt_button = gr.Button(value='Stop', variant='stop', interactive=True, visible=True)

        with gr.Column():
            with gr.Column():

                gr.Markdown('## Options')
                with gr.Row():

                    with gr.Column():
                        gr.Markdown('#### Processing Options')
                        gr.Markdown('''These toggles control which processes to run on your input text. 
                        Unchecking them will also mean that they will not be rendered in the final output, 
                        regardless of the output options below''')

                        run_options_jishoparse = gr.Checkbox(value=True, label='JishoParse', info='Perform sentence parsing using Jisho', container=True, interactive=True)
                        run_options_tts = gr.Checkbox(value=True, label='Text-to-Speech', info='Enable Text-to-Speech', container=True, interactive=True)
                        run_options_preprocess = gr.Checkbox(value=True, label='Preprocess', info='Use preprocessed text for translation', container=True, interactive=True)
                        run_options_deepl_tl = gr.Checkbox(value=True, label='DeepL TL', info='Translate using DeepL', container=True, interactive=True)
                        run_options_google_tl = gr.Checkbox(value=True, label='Google TL', info='Translate using Google', container=True, interactive=True)
                        run_options_clean_post_split = gr.Checkbox(value=True, label='Clean Clauses', info='Remove trailing punctuation marks when sentences are split into clauses', container=True, interactive=True)

                    with gr.Column():
                        gr.Markdown('#### Processing Levels')
                        with gr.Group():
                            text_options_deepl = gr.CheckboxGroup(choices=[('Para', 'para'), ('Lines', 'line'), ('Clauses', 'clauses')], label='DeepL Translate:', value=['line', 'clauses'], interactive=True)
                            text_options_use_prepro_deepl = gr.Checkbox(value=True, label='Use Preprocessed for Deepl TL', container=True, interactive=True)
                        with gr.Group():
                            text_options_google_tl = gr.CheckboxGroup(choices=[('Para','para'), ('Lines', 'line'), ('Clauses', 'clauses')], label='Google Translate:', value=['line', 'clauses'], interactive=True)
                            text_options_use_prepro_google_tl = gr.Checkbox(value=True, label='Use Preprocessed for Google TL', container=True, interactive=True)


                    with gr.Column():
                        gr.Markdown('#### Output Options')
                        with gr.Group():
                            output_options_include_jisho_parse = gr.Checkbox(value=True, label='Jisho Parse', container=True, interactive=True)
                            output_options_include_clause_analysis = gr.Checkbox(value=True, label='Clause Analysis', container=True, interactive=True)

                        with gr.Group():
                            output_options_also_output_single_file = gr.Checkbox(value=False, label='Output Single File version', info='Generate a single self contained HTML in addition to regular output', interactive=True  )
                        # output_options_include_clause_analysis = gr.Checkbox(value=True, label='Clause Analysis', container=True, interactive=True)
                        # output_options_include_clause_analysis = gr.Checkbox(value=True, label='Clause Analysis', container=True, interactive=True)
                        # output_options_include_clause_analysis = gr.Checkbox(value=True, label='Clause Analysis', container=True, interactive=True)

                        pass


                # with gr.Row():
                with gr.Row():
                    rekai_html_log_area = gr.Textbox(label='Log', value='', lines=10, max_lines=20, visible=True, interactive=False)

    with gr.Tab("Settings") as preprocess_tab:
        with gr.Column():
            pass



    ## Event Listeners (backend)
    run_main = html_generate_button.click(fn=main, inputs=[raw_input_text_box, preprocessed_input_text_box, html_header_input_textbox])
    interrupt_main = html_interrupt_button.click(fn=None, cancels=run_main)


if __name__ == '__main__':

    demo.launch()