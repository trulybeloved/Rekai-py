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

import gradio as gr


from appconfig import AppConfig, RunConfig
from custom_dataclasses import RekaiText
from processors import Process
from generators import GenerateHtml
from custom_modules.utilities import get_current_timestamp
from custom_modules.utilities import log_process_time
import data_for_processing
# ----------------------------------------------------------------------------------------------------------------------#
# GLOBAL VARIABLES
# ----------------------------------------------------------------------------------------------------------------------#


# ----------------------------------------------------------------------------------------------------------------------#
# GRADIO WEBGUI
# ----------------------------------------------------------------------------------------------------------------------#

class CustomTest:
    """Just a temporary class with methods for quick testing of the backend"""

    @staticmethod
    @log_process_time
    def rekai_test():

        input_raw = data_for_processing.small_sample
        input_prepro = data_for_processing.input_preprocessed

        timestamp = get_current_timestamp()
        output_directory = AppConfig.output_directory

        final_output_path = os.path.join(output_directory, f'Rekai_HTML_{timestamp}')

        run_config = RunConfig()

        rekai_text_object = RekaiText(input_text=input_raw, input_preprocessed_text=input_prepro, run_config_object=run_config, text_header='HEADER')

        if run_config.run_jisho_parse:
            Process.jisho_parse(rekai_text_object=rekai_text_object)
        if run_config.run_tts:
            Process.gcloud_tts(rekai_text_object=rekai_text_object)
        if run_config.run_deepl_tl:
            Process.deepl_tl(rekai_text_object=rekai_text_object)
        if run_config.run_google_tl:
            Process.google_tl(rekai_text_object=rekai_text_object)

        GenerateHtml.RekaiHtml.full_html(run_config_object=run_config, input_rekai_text_object=rekai_text_object,
                                         html_title='Rekai_Test', output_directory=final_output_path, post_process=None,
                                         single_file_mode=False)

        if run_config.output_single_file:
            GenerateHtml.RekaiHtml.full_html(run_config_object=run_config, input_rekai_text_object=rekai_text_object,
                                             html_title='Rekai_Test', output_directory=final_output_path,
                                             post_process=None,
                                             single_file_mode=True)





# Main Function
def main(japanese_text, preprocessed_text, header):

    timestamp = get_current_timestamp()

    output_directory = AppConfig.output_directory

    run_config = RunConfig()

    final_output_path = os.path.join(output_directory, f'Rekai_HTML_{timestamp}')

    rekai_text_object = RekaiText(input_text=japanese_text, input_preprocessed_text=preprocessed_text, run_config_object=run_config, text_header=header)

    if run_config.run_jisho_parse:
        Process.jisho_parse(rekai_text_object=rekai_text_object)
    if run_config.run_tts:
        Process.gcloud_tts(rekai_text_object=rekai_text_object)
    if run_config.run_deepl_tl:
        Process.deepl_tl(rekai_text_object=rekai_text_object)
    if run_config.run_google_tl:
        Process.google_tl(rekai_text_object=rekai_text_object)

    GenerateHtml.RekaiHtml.full_html(run_config_object=run_config, input_rekai_text_object=rekai_text_object,
                                     html_title='Rekai_Test', output_directory=final_output_path, post_process=None, single_file_mode=False)

    if run_config.output_single_file:
        GenerateHtml.RekaiHtml.full_html(run_config_object=run_config, input_rekai_text_object=rekai_text_object,
                                         html_title='Rekai_Test', output_directory=final_output_path, post_process=None,
                                         single_file_mode=True)


# Frontend
with gr.Blocks() as webgui:
    gr.Markdown("""# Re:KAI""")

    with gr.Tab('RekaiHTML') as rekai_html_tab:

        gr.Markdown('''Generate RekaiHTML files for japanese text.''')

        with gr.Row():
            with gr.Column():
                html_header_input_textbox = gr.Textbox(label='Header', lines=1, max_lines=2, visible=True, interactive=True)

                raw_input_text_box = gr.Textbox(label='Japanese Raw Text', value='', lines=10, max_lines=20, visible=True, interactive=True,
                                                 placeholder='Input Japanese Raw text here')

                preprocessed_input_text_box = gr.Textbox(label='Preprocessed Text', value='', lines=10, max_lines=20,
                                                 visible=True, interactive=True,
                                                 placeholder='Input Preprocessed text here')

                html_generate_button = gr.Button(value='Generate HTML', variant='primary', interactive=True, visible=True)

                html_interrupt_button = gr.Button(value='Stop', variant='stop', interactive=False, visible=True)

            with gr.Column():

                # with gr.Row():
                with gr.Row():
                    rekai_html_log_area = gr.Textbox(label='Log', value='', lines=10, max_lines=20, visible=True, interactive=False)

    with gr.Tab("Preprocess") as preprocess_tab:
        with gr.Column():
            Tab0_run_btn = gr.Button('Run')

    ## Event Listeners
    html_generate_button.click(fn=main, inputs=[raw_input_text_box, preprocessed_input_text_box, html_header_input_textbox])


if __name__ == '__main__':

    # webgui.launch()
    CustomTest.rekai_test()