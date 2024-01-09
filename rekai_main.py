# -*- coding: utf-8 -*-

"""
@author: beloved

This app will take japanese text as input, carry out all the NLP tasks, and save everything in a structured database
along with media files in proper folders, uniquely named folders.

Features:
- gradio UI for interfacing
- inputs - Option to input the respective text lines or
- JP text line spliting
- Incorporate Kudasai Preprocessor
-

Todo

- There should be a central DB for all the lines that have been run and sucessfully processed. - sqlite will work
- Add check for internet connectivity
- add assertion error try accept blocks to data processing pipelines
- improve unparsability check
- add paragraph classifier
"""
import os.path

import gradio as gr

from Rekai.appconfig import AppConfig
from Rekai.custom_dataclasses import RekaiText
from Rekai.processors import Process
from Rekai.generators import GenerateHtml
from Rekai.custom_modules.utilities import get_current_timestamp
# ----------------------------------------------------------------------------------------------------------------------#
# GLOBAL VARIABLES
# ----------------------------------------------------------------------------------------------------------------------#


# ----------------------------------------------------------------------------------------------------------------------#
# GRADIO WEBGUI
# ----------------------------------------------------------------------------------------------------------------------#

class CustomTest:
    @staticmethod
    def rekai_test():
        input_japanese_text = '''
        
「休日、なのにどうしてこんな騒ぎに巻き込まれたの？」



「それは少しだけ複雑なのですが……そこの、スバルの導きですね」



　今は意識がここにない少年、彼との出会いがラインハルトをここへ導いたのだ。

　順を追って説明すれば、ラインハルトがスバルと初めて邂逅した路地裏、あそこでのスバルとの問答にまで物語はさかのぼる。

　あのとき、スバルは『銀髪で白いローブを着た女性を探している』とラインハルトに漏らしていた。あの時点で、ラインハルトの知識に該当する人物はひとりしかいない。

　その人物への接触を求めるスバル。彼の動向を探るうちに、ラインハルトもまた、貧民街へと足を踏み入れることとなり、



「途中で彼女と出会い、今に至るというところです」



「そう、あの子に」
        '''
        timestamp = get_current_timestamp()
        output_directory = AppConfig.output_directory

        final_output_path = os.path.join(output_directory, f'Rekai_HTML_{timestamp}')

        rekai_text_object = RekaiText(input_text=input_japanese_text)

        Process.jisho_parse(input_rekai_text_object=rekai_text_object)
        Process.gcloud_tts(input_rekai_text_object=rekai_text_object)

        GenerateHtml.RekaiHtml.full_html(input_rekai_text_object=rekai_text_object, html_title='Rekai_Test', output_directory=final_output_path)

class RekaiUI:

    def gradio_web_ui(self):

        # Frontend
        with gr.Blocks() as self.web_ui:
            gr.Markdown("""# Re:KAI""")

            with gr.Tab("Preprocess") as self.preprocess_tab:
                with gr.Column():
                    Tab1_run_btn = gr.Button('Run')

            # Event Listeners


    def launch(self):
        self.gradio_web_ui()
        self.web_ui.launch(show_error=True)


if __name__ == '__main__':

    try:
        CustomTest.rekai_test()
    except Exception as e:
        print(e)
