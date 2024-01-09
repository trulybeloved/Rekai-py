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



import gradio as gr


# ----------------------------------------------------------------------------------------------------------------------#
# GLOBAL VARIABLES
# ----------------------------------------------------------------------------------------------------------------------#


# ----------------------------------------------------------------------------------------------------------------------#
# GRADIO WEBGUI
# ----------------------------------------------------------------------------------------------------------------------#


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
        rekai_ui = RekaiUI()
        rekai_ui.launch()
    except Exception as e:
        print(e)
