## built-in libraries
import json
from typing import Union

import base64
import os.path
import shutil

## third-party libraries
from loguru import logger
from bs4 import BeautifulSoup

import minify_html

## custom modules
from custom_dataclasses import RekaiText, Paragraph, Line, Clause
from appconfig import AppConfig, RunConfig
from custom_modules.utilities import FileManagement, decode_bytes_from_base64_string


class HtmlUtilities:

    @staticmethod
    def minify(input_code: str) -> str:
        """Can minify css and js as well"""
        minifed_code = minify_html.minify(code=input_code, do_not_minify_doctype=True)
        return minifed_code

    @staticmethod
    def prettify_html(input_html: str) -> str:
        soup = BeautifulSoup(input_html, 'html.parser')
        prettified_html = soup.prettify()
        return prettified_html

    @staticmethod
    def get_css():
        css_path = AppConfig.path_to_css_source
        try:
            with open(file=css_path, mode='r', encoding='utf-8') as file:
                css_content = file.read()
                return css_content
        except FileNotFoundError:
            logger.error(f"Error: The file {css_path} was not found.")
        except Exception as e:
            logger.exception(f"Error: An unexpected error occurred - {str(e)}")

    @staticmethod
    def get_js():
        css_path = AppConfig.path_to_js_source
        try:
            with open(file=css_path, mode='r', encoding='utf-8') as file:
                js_content = file.read()
                return js_content
        except FileNotFoundError:
            logger.error(f"Error: The file {css_path} was not found.")
        except Exception as e:
            logger.exception(f"Error: An unexpected error occurred - {str(e)}")


class GenerateHtml:
    class Config:
        pass

    class CommonElements:

        copy_button_content = '''<span style="font-size: .875em; margin-right: .125em; position: relative; top: -.25em; left: -.125em">📄<span style="position: absolute; top: .25em; left: .25em">📄</span></span>Raw'''
        copy_button_content_prepro = '''<span style="font-size: .875em; margin-right: .125em; position: relative; top: -.25em; left: -.125em">📄<span style="position: absolute; top: .25em; left: .25em">📄</span></span>PrePro'''
        copy_button_content_edited = '''<span style="font-size: .875em; margin-right: .125em; position: relative; top: -.25em; left: -.125em">📄<span style="position: absolute; top: .25em; left: .25em">📄</span></span>Edited'''
        audio_button_content = '''▶ TTS'''

    class FileOutput:

        @staticmethod
        def tts(line_id: str, line_tts_b64_str: str, output_directory: str) -> str:
            tts_file_extension = AppConfig.tts_file_extension
            tts_bytes = decode_bytes_from_base64_string(line_tts_b64_str)
            tts_file_name = f'{line_id}_tts.{tts_file_extension}'
            tts_save_path = os.path.join(output_directory, tts_file_name)
            with open(tts_save_path, 'wb') as tts_output_file:
                tts_output_file.write(tts_bytes)

            return tts_file_name

        @staticmethod
        def associated_files(output_directory: str) -> None:
            source_directory = AppConfig.path_to_rekai_html_src
            destination_directory = output_directory
            try:
                shutil.copytree(src=source_directory, dst=destination_directory)
            except shutil.Error as e:
                logger.exception(e)
            except Exception as e:
                logger.exception(e)

    class RekaiHtmlBlock:

        # Run configuration
        config_preprocess: bool

        config_include_jisho_parse: bool
        config_include_tts: bool

        config_include_preprocessed_para: bool
        config_set_preprocessed_para_as_default: bool
        config_include_preprocessed_line: bool

        config_include_line_deepl_tl: bool
        config_include_line_google_tl: bool
        config_include_clause_analysis: bool
        config_include_clause_deepl_tl: bool
        config_include_clause_google_tl: bool

        single_file_mode: bool

        def __init__(self, run_config_object: RunConfig, single_file_mode: bool):
            self.set_config(run_config_object=run_config_object)
            self.single_file_mode = single_file_mode
            self.rekai_text_object = None

        def set_config(self, run_config_object: RunConfig):

            self.config_preprocess = run_config_object.preprocess

            self.config_include_jisho_parse = (run_config_object.run_jisho_parse
                                               and run_config_object.include_jisho_parse)

            self.config_include_tts = run_config_object.run_tts

            self.config_include_preprocessed_para = run_config_object.preprocess

            self.config_set_preprocessed_para_as_default = run_config_object.use_preprocessed_for_paragraphs

            self.config_include_preprocessed_line = run_config_object.preprocess

            self.config_include_line_deepl_tl = (run_config_object.run_deepl_tl
                                                 and run_config_object.deepl_tl_lines)

            self.config_include_line_google_tl = (run_config_object.run_google_tl
                                                  and run_config_object.google_tl_lines)

            self.config_include_clause_analysis = run_config_object.include_clause_analysis

            self.config_include_clause_deepl_tl = (run_config_object.include_clause_analysis
                                                   and run_config_object.deepl_tl_clauses)

            self.config_include_clause_google_tl = (run_config_object.include_clause_analysis
                                                    and run_config_object.google_tl_clauses)

        # Inner Elements ===========================================
        def audio_button(self, line_id: str, line_tts_b64_str: str, output_directory: str) -> str:

            tts_file_output_folder_name = AppConfig.tts_output_folder_name
            tts_file_output_directory_path = os.path.join(output_directory, tts_file_output_folder_name)
            tts_file_name = GenerateHtml.FileOutput.tts(line_id=line_id, line_tts_b64_str=line_tts_b64_str,
                                                        output_directory=tts_file_output_directory_path)
            line_tts_relative_path = f'{tts_file_output_folder_name}/{tts_file_name}'

            if self.single_file_mode:
                base64ogg = line_tts_b64_str

                output_html = f'''
                <audioButton id="{line_id}-tts-button" class="audioButton audioButton-play">{GenerateHtml.CommonElements.audio_button_content}
                </audioButton>
                <div id="{line_id}-audioPlayer" class="audioPlayer"
                    src="{line_tts_relative_path}" base64ogg="{base64ogg}"></div>
                '''
            else:

                output_html = f'''
                <audioButton id="{line_id}-tts-button" class="audioButton audioButton-play">{GenerateHtml.CommonElements.audio_button_content}
                </audioButton>
                <div id="{line_id}-audioPlayer" class="audioPlayer"
                    src="{line_tts_relative_path}"></div>
                '''

            return output_html

        # Card Blocks ==============================================
        def para_card_unparsable(self, paragraph_number: int, input_rekai_paragraph_object: Paragraph) -> str:

            paragraph_object = input_rekai_paragraph_object
            paragraph_id = f'P{paragraph_number}'
            paragraph_raw = paragraph_object.raw_text

            # PARA CARD START
            output_html = f'<div id="{paragraph_id}" class="para-card unparsable">'  # Unparsable class added

            # PARA CARD HEADER
            output_html += f''' 
               <div class="para-card-header">
                   <div class="card-header-left-half">
                       <div class="card-para-number"><span>{paragraph_number}</span></div>
                       <div class="card-para-type"><span>{paragraph_object.paragraph_type}</span></div>
                   </div>
                   <div class="card-header-right-half">
                       <button id="{paragraph_id}-copy-button" class="raw-copy-button raw-para-copy-button"
                           onclick="copyTextByElementId('{paragraph_id}-raw-text', '{paragraph_id}-copy-button')">{GenerateHtml.CommonElements.copy_button_content}</button>
                   </div>
               </div>'''

            # PARA CARD CONTENTS
            output_html += f'''
                <div class="card-contents-raw master-raw">
                    <div id="{paragraph_id}-raw-text" class="card-contents-raw-text">
                    <span class="japanese-raw-para">{paragraph_raw}</span>
                    </div>
                </div>'''

            # PARA CARD END
            output_html += f'</div>'

            return output_html

        def clause_card_lables(self) -> str:

            output_html = '<div class="clause-card-label-container">'

            if self.config_preprocess:
                default_label = 'Preprocessed'
            else:
                default_label = 'Raw'

            output_html += f'<div class="clause-card-label">{default_label}</div>'

            if self.config_include_clause_deepl_tl:
                output_html += f'<div class="clause-card-label">DeepL</div>'

            if self.config_include_clause_google_tl:
                output_html += f'<div class="clause-card-label">Google</div>'

            output_html += '</div>'

            return output_html

        def clause_card(self, paragraph_number: int, line_number: int, clause_number: int,
                        input_rekai_clause_object: Clause) -> str:

            clause_object = input_rekai_clause_object
            clause_id = f'P{paragraph_number}_L{line_number}_C{clause_number}'
            clause_raw = clause_object.raw_text
            clause_preprocessed = clause_object.preprocessed_text

            # If clause analysis is enabled, include the clause split structure by default.
            output_html = f'''<div id="{clause_id}" class="clause-card">'''

            # If preprocess option is enabled, use preprocessed japanese text to query the db, else use raw
            if self.config_preprocess:
                clause_key = clause_preprocessed
                output_html += f'''<div id="{clause_id}-input" class="clause-subcard subcard-contents-preprocessed copy-on-click">{clause_preprocessed}</div>'''
            else:
                clause_key = clause_raw
                output_html += f'''<div id="{clause_id}-input" class="clause-subcard subcard-contents-preprocessed copy-on-click">{clause_raw}</div>'''

            if self.config_include_clause_deepl_tl:
                clause_deepl_tl = clause_object.tl_deepl
                output_html += f'''<div id="{clause_id}-deepl_tl" class="clause-subcard subcard-contents-deepl copy-on-click">{clause_deepl_tl}</div>'''

            if self.config_include_clause_google_tl:
                clause_google_tl = clause_object.tl_google
                output_html += f'''<div id="{clause_id}-google_tl" class="clause-subcard subcard-contents-googletl copy-on-click">{clause_google_tl}</div>'''

            # END OF CLAUSE CARD
            output_html += f'</div>'

            return output_html

        def line_card(self, paragraph_number: int, line_number: int, input_rekai_line_object: Line,
                      output_directory: str, total_lines: int) -> str:

            paragraph_id = f'P{paragraph_number}'
            line_object = input_rekai_line_object
            line_id = f'P{paragraph_number}_L{line_number}'
            line_raw = line_object.raw_text
            line_preprocessed = line_object.preprocessed_text

            if self.config_include_tts:
                audio_button_html = self.audio_button(line_id=line_id, line_tts_b64_str=line_object.tts_b64_str,
                                                      output_directory=output_directory)
            else:
                audio_button_html = ''

            # CARD SLAVE START
            output_html = f'<div id="{line_id}" class="line-card" style="display: none;">'

            # CARD SLAVE HEADER
            output_html += f'''
                <div class="line-card-header">
                    <div class="card-header-left-half">
                        <div class="card-line-number" onclick="expandCollapseLineContents('{line_id}')">P{paragraph_number}: Line {line_number} of {total_lines}</div>
                    </div>

                    <div class="card-header-right-half">
                        <button id="{line_id}-copy-button" class="raw-copy-button raw-line-copy-button"
                            onclick="copyTextByElementId('{line_id}-raw-text', '{line_id}-copy-button')">{GenerateHtml.CommonElements.copy_button_content}</button>
                        {audio_button_html}
                    </div>
                </div>
            '''

            # LINE CARD CONTENTS START
            output_html += f'''<div class="line-card-contents-container">'''

            # CARD TTS WAVESURFER WAVEFORM
            output_html += f'''                        
                <div class="line-card-audio-container">
                    <div class="audio-waveform" id="waveform-{line_id}"></div>
                    <div class="audio-hover"></div>
                    <div class="time"></div>
                    <div class="duration"></div>
                </div>
                '''

            if self.config_include_jisho_parse:
                jisho_parsed_html = line_object.jisho_parse_html
                # CARD SLAVE JISHO PARSE
                output_html += f'''
                    <div id="{line_id}-jisho-parse" class="card-contents-jisho-parse">
                        <div class="card-contents-jisho-parse-text">
                        {jisho_parsed_html}
                        </div>
                    </div>        
                '''

            # CARD SLAVE RAW
            output_html += f'''
                <div class="card-contents-raw slave-raw">
                    <div id="{line_id}-raw-text" class="card-contents-raw-text copy-on-click">
                    <span class="japanese-raw-line">{line_raw}</span>
                    </div>
                </div>
            '''

            if self.config_preprocess:
                line_key = line_preprocessed
            else:
                line_key = line_raw

            # LINE CARD PREPROCESSED
            if self.config_include_preprocessed_line:
                output_html += f'''
                <div class="line-preprocessed-container">
                    <div class="line-content-label">Preprocessed</div>
                    <div class="card-contents-line-preprocessed copy-on-click" id={line_id}-preprocessed)">{line_preprocessed}</div>
                </div>
                '''
            # LINE CARD FULL DEEPL TL
            if self.config_include_line_deepl_tl:
                line_deepl_tl = line_object.tl_deepl
                output_html += f'''
                <div class="line-deepl-container">
                    <div class="line-content-label">DeepL</div>
                    <div class="card-contents-line-deepl copy-on-click" id={line_id}-deepl)">{line_deepl_tl}</div>
                </div>
                '''

            # LINE CARD FULL GOOGLE TL
            if self.config_include_line_google_tl:
                line_google_tl = line_object.tl_google
                output_html += f'''
                <div class="line-google-tl-container">
                    <div class="line-content-label">Google</div>
                    <div class="card-contents-line-google-tl copy-on-click" id={line_id}-google-tl)">{line_google_tl}</div>
                </div>
                '''

            # CLAUSE CARD CONTAINER START
            output_html += '''<div class="clause-card-container">'''

            # LINE CARD CLAUSE BY CLAUSE
            if self.config_include_clause_analysis:
                if line_object.is_single_clause():
                    pass
                else:
                    # CLAUSE ANALYSIS CARD LABELS
                    output_html += f'{self.clause_card_lables()}'

                    # CLAUSE CARDS
                    for (clause_number, clause_object) in line_object.numbered_clause_objects:
                        output_html += f'{self.clause_card(paragraph_number=paragraph_number, line_number=line_number, clause_number=clause_number, input_rekai_clause_object=clause_object)}'

            # CLAUSE CARD CONTAINER END
            output_html += '''</div>'''

            # LINE CARD CONTENTS CONTAINER END
            output_html += '''</div>'''

            # LINE CARD END
            output_html += f'''
            </div>'''

            return output_html

        def para_card_header(self, paragraph_number: int, paragraph_id: str,
                             input_rekai_paragraph_object: Paragraph) -> str:

            paragraph_object = input_rekai_paragraph_object

            # Conditionally assigns a class to the paragraph label based on the para type
            if paragraph_object.is_dialogue:
                label_class = 'dialogue-label'
            elif paragraph_object.is_narration:
                label_class = 'narration-label'
            else:
                label_class = ''

            output_html = f''' 
               <div class="para-card-header">
                   <div class="card-header-left-half">
                       <div class="card-para-number"><span>{paragraph_number}</span></div>
                       <div class="card-para-type {label_class}"><span>{paragraph_object.paragraph_type}</span></div>
                   </div>
                        <div class=card-header-mid-section>
                        <div class="expand-collapse-button" onclick="expandCollapseCard('{paragraph_id}')">Expand</div>
                        </div>
                   <div class="card-header-right-half">
                        <button id="{paragraph_id}-prepro-copy-button" class="raw-copy-button raw-para-copy-button"
                           onclick="copyTextByElementId('{paragraph_id}-prepro-text', '{paragraph_id}-prepro-copy-button')">{GenerateHtml.CommonElements.copy_button_content_prepro}</button>
                       <button id="{paragraph_id}-copy-button" class="raw-copy-button raw-para-copy-button"
                           onclick="copyTextByElementId('{paragraph_id}-raw-text', '{paragraph_id}-copy-button')">{GenerateHtml.CommonElements.copy_button_content}</button>
                   </div>
               </div>'''

            return output_html

        def para_card(self, paragraph_number: int, input_rekai_paragraph_object: Paragraph,
                      output_directory: str) -> str:

            paragraph_object = input_rekai_paragraph_object
            paragraph_id = f'P{paragraph_number}'
            paragraph_raw = paragraph_object.raw_text
            line_count = input_rekai_paragraph_object.line_count

            no_display_style_tag = ''' style="display: none;" '''

            # PARA CARD START
            output_html = f'<div id="{paragraph_id}" class="para-card">'

            # PARA CARD HEADER
            output_html += self.para_card_header(paragraph_number=paragraph_number, paragraph_id=paragraph_id,
                                                 input_rekai_paragraph_object=input_rekai_paragraph_object)

            # If adding container for para card contents, ensure to change addParaContentExpandOnClickEvent() in JS
            # PARA CARD CONTENTS
            if self.config_set_preprocessed_para_as_default:
                paragraph_preprocessed = paragraph_object.preprocessed_text
                # RAW
                output_html += f'''
                    <div class="card-contents-raw master-raw" {no_display_style_tag}>
                        <div id="{paragraph_id}-raw-text" class="card-contents-raw-text">
                        <span class="japanese-raw-para">{paragraph_raw}</span>
                        </div>
                    </div>'''
                # PREPROCESSED
                output_html += f'''
                    <div class="card-contents-prepro master-preprocessed">
                        <div id="{paragraph_id}-prepro-text" class="card-contents-prepro-text">
                        <span class="japanese-preprocessed-para">{paragraph_preprocessed}</span>
                        </div>
                    </div>'''
            else:
                # RAW
                output_html += f'''
                    <div class="card-contents-raw master-raw">
                        <div id="{paragraph_id}-raw-text" class="card-contents-raw-text">
                        <span class="japanese-raw-para">{paragraph_raw}</span>
                        </div>
                    </div>'''
                # PREPROCESSED
                if self.config_preprocess:
                    paragraph_preprocessed = paragraph_object.preprocessed_text
                    output_html += f'''
                    <div class="card-contents-prepro master-preprocessed" {no_display_style_tag}>
                        <div id="{paragraph_id}-prepro-text" class="card-contents-prepro-text">
                        <span class="japanese-preprocessed-para">{paragraph_preprocessed}</span>
                        </div>
                    </div>'''

            # LINE CARD CONTAINER START
            output_html += '''<div class="line-card-container collapsed">'''

            # GENERATE SLAVE CARDS
            for (line_number, line_object) in input_rekai_paragraph_object.numbered_line_objects:
                output_html += f'{self.line_card(paragraph_number=paragraph_number, line_number=line_number, input_rekai_line_object=line_object, output_directory=output_directory, total_lines=line_count)}'

            # PARACARD LOWER COLLAPSE BUTTON
            output_html += f'''
            <div class="expand-collapse-button" onclick="expandCollapseCard('{paragraph_id}')">Collapse</div>
            '''
            #
            # # PARACARD LOWER COLLAPSE BUTTON
            # output_html += f'''
            # <div class="para-card-collapse-button-container">
            # <div class="expand-collapse-button" onclick="expandCollapseCard('{paragraph_id}')">Collapse</div>
            # </div>'''
            #
            # # LINE CARD CONTAINER END
            output_html += '''</div>'''

            # PARA CARD END
            output_html += f'</div>'

            return output_html

        # Page Blocks ==============================================
        def html_head(self, html_title: str) -> str:

            if self.single_file_mode:
                stylesheet = HtmlUtilities.get_css()
                style_tag = f'''<style>{stylesheet}</style>'''
            else:
                style_tag = f'''<link rel="stylesheet" href="css/styles.css">'''

            html_head = f'''
            <!DOCTYPE html>
            <html>

            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{html_title}</title>

                <link rel="preconnect" href="https://fonts.googleapis.com">
                <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                <link rel="stylesheet"
                    href="https://fonts.googleapis.com/css2?family=Roboto:wght@100;300;400;500;700;900&display=swap">
                {style_tag}
            </head>
            '''
            return html_head

        def html_body_prefix(self, ) -> str:
            output_html = f'''<body><main><div id="primary" class="primary">'''
            return output_html

        def html_body_main(self, input_rekai_text_object: RekaiText, output_directory: str) -> str:

            self.rekai_text_object = input_rekai_text_object

            output_html = '<div id="card-coloumn" class="card-coloumn">'

            for (index, paragraph_object) in input_rekai_text_object.numbered_paragraph_objects:
                if paragraph_object.unparsable:
                    output_html += self.para_card_unparsable(
                        input_rekai_paragraph_object=paragraph_object,
                        paragraph_number=index)
                else:
                    output_html += self.para_card(
                        input_rekai_paragraph_object=paragraph_object,
                        paragraph_number=index,
                        output_directory=output_directory)

            output_html += '</div>'

            return output_html

        def html_body_suffix(self, top_bar_title: str) -> str:

            if self.single_file_mode:
                javascript = HtmlUtilities.get_js()
                script_tag = f'''<script>{javascript}</script>'''
            else:
                script_tag = f'''<script src="javascript/rekai.js"></script>'''

            analytics_tag = '''<!-- Cloudflare Web Analytics --><script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "88f1749ec8c14ec185b8a86a3164cc5a"}'></script><!-- End Cloudflare Web Analytics -->'''

            output_html = f'''
                     <!-- SIDEBAR --------------------------------------------------------------------->
                        <div id="sidebar-placeholder" class="sidebar-placeholder">
                            <div id="right-sidebar" class="right-sidebar sidebar-expanded">
                            
                                <div class="sidebar-tab-buttons">
                                    <div id="jisho-tab-button" class="tab-button tab-button-generic" onclick="showTab('#jisho-iframe-container')">Jisho</div>
                                    <div id="chapter-search-tab-button" class="tab-button tab-button-generic" onclick="showTab('#chapter-search-iframe-container')">Chapter Search</div>
                                </div>

                                <div id="jisho-iframe-container" class="sidebar-tab right-sidebar-iframe-container">
                                    <iframe class=sidebar-iframe id=sidebar-iframe name=sidebar-iframe src=https://jisho.org/ frameborder="0"></iframe>
                                </div>

                                <div id="chapter-search-iframe-container" class="sidebar-tab chapter-search-iframe-container">
                                    <iframe class=chapter-search-iframe id=chapter-search-iframe name=sidebar-chapter-search-iframe src="https://re-zero-chapter-search-ui.web.app/" frameborder="0"></iframe>
                                </div>                           
                                
                            </div>
                        </div>
                    </div> 
                </main>

                <!-- TOP BAR --------------------------------------------------------------------->
                <div id="top-bar" class="top-bar">
                    <div class="top-bar-flex-container">
                        <div class="top-bar-start-section">
                            <div class="top-bar-title">
                                <div>RE:KAI</div>
                            </div>
                            <div class="top-bar-chapter-title">
                                <div>{top_bar_title}</div>
                            </div>
                        </div>
                        <div class="top-bar-mid-section">
                            <span>Toggles:</span>
                            <!-- function toggleElementDisplay(buttonId, elementClass, displayType, showText, hideText) -->
                            <button id="toggle-raw-para-button" class="top-bar-button top-bar-button-generic"
                                onclick="toggleDisplay(this,'.card-contents-raw.master-raw','flex')">PRaw</button>
                            
                            <button id="toggle-prepro-para-button" class="top-bar-button top-bar-button-generic"
                                onclick="toggleDisplay(this,'.card-contents-prepro.master-preprocessed','flex')">PPrePro</button>

                            <button id="toggle-prepro-button" class="top-bar-button top-bar-button-generic"
                                onclick="toggleDisplay(this,'.card-contents-jisho-parse','flex')">JParse</button>
                            
                            <button id="toggle-raw-line-button" class="top-bar-button top-bar-button-generic"
                                onclick="toggleDisplay(this,'.card-contents-raw.slave-raw','flex')">LRaw</button>                                

                            <button id="toggle-prepro-button" class="top-bar-button top-bar-button-generic"
                                onclick="toggleDisplay(this,'.line-preprocessed-container','block')">LPrePro</button>

                            <button id="toggle-deepl-button" class="top-bar-button top-bar-button-generic"
                                onclick="toggleDisplay(this,'.line-deepl-container','block')">DeepL</button>

                            <button id="toggle-google-button" class="top-bar-button top-bar-button-generic"
                                onclick="toggleDisplay(this,'.line-google-tl-container','block')">Google</button>
                            
                            <button id="toggle-clauses-button" class="top-bar-button top-bar-button-generic"
                                onclick="toggleDisplay(this,'.clause-card-container','block')">Clauses</button>

                            <button id="toggle-waveform-button" class="top-bar-button top-bar-button-generic"
                                onclick="toggleDisplay(this,'.line-card-audio-container','flex')">Waveform</button>
                                
                            <span>||</span>
                            
                            <button id="expand-all-paras" class="top-bar-button top-bar-button-generic"
                                onclick="expandAllParas()">Expand All</button>
                                
                            <button id="collapse-all-paras" class="top-bar-button top-bar-button-generic"
                                onclick="collapseAllParas()">Collapse All</button>
                        </div>
                        <div class="top-bar-end-section">
                            <button id="toggle-light-dark-mode-button" class="top-bar-button top-bar-button-generic" onclick="toggleDarkMode()">Light|Dark</button>
                            <button id="toggle-sidebar-button" class="top-bar-button top-bar-button-generic" onclick="toggleRightSidebar()">Hide Omnibar</button>
                        </div>
                    </div>
                </div>

                <!-- SCRIPT --------------------------------------------------------------------->
                {script_tag}     
                {analytics_tag}           
            </body>
            </html>
            '''
            return output_html

    class RekaiHtml:
        @staticmethod
        def full_html(run_config_object: RunConfig, html_title: str, input_rekai_text_object: RekaiText,
                      output_directory: str, post_process: Union[str, None], single_file_mode: bool) -> str:

            if not single_file_mode:
                GenerateHtml.FileOutput.associated_files(output_directory=output_directory)

            generate = GenerateHtml.RekaiHtmlBlock(run_config_object=run_config_object,
                                                   single_file_mode=single_file_mode)

            html = generate.html_head(html_title=html_title)
            html += generate.html_body_prefix()
            html += generate.html_body_main(input_rekai_text_object=input_rekai_text_object,
                                            output_directory=output_directory)
            html += generate.html_body_suffix(top_bar_title=input_rekai_text_object.text_header)

            if post_process == 'prettify':
                html = HtmlUtilities.prettify_html(html)
            elif post_process == 'minify':
                html = HtmlUtilities.minify(html)

            if single_file_mode:
                file_name_suffix = '_single_file'
            else:
                file_name_suffix = ''

            output_html_file_path = os.path.join(output_directory, f'index{file_name_suffix}.html')

            with open(output_html_file_path, 'w', encoding='utf-8') as rekai_html_file:
                rekai_html_file.write(html)

            # Zip file export
            zip_file_name = f'Rekai_HTML_{run_config_object.run_timestamp}_{html_title}'
            zip_file_path = FileManagement.zip_directory(output_directory, zip_file_name, AppConfig.output_directory)

            os.startfile(output_html_file_path)

            logger.info('RekaiHTML file generated successfully')

            return zip_file_path


class GenerateRekaiPortable:
    @staticmethod
    def rekai_json(input_rekai_text_object: RekaiText):

        rekai_output_dict = dict()
        rekai_tts_output_list = list()
        rekai_output_dict['rekai_header'] = input_rekai_text_object.text_header
        rekai_output_dict['preprocessed_available'] = input_rekai_text_object.preprocessed_available
        rekai_output_dict['total_paragraph_count'] = input_rekai_text_object.paragraph_count

        rekai_output_dict['paragraphs'] = list()

        for (index, paragraph_object) in input_rekai_text_object.numbered_paragraph_objects:
            paragraph_dict = dict()
            paragraph_dict['paragraph_number'] = index
            paragraph_dict['paragraph_id'] = f'P{index}'
            paragraph_dict['paragraph_type'] = paragraph_object.paragraph_type
            paragraph_dict['is_unparsable'] = paragraph_object.unparsable
            paragraph_dict['paragraph_raw'] = paragraph_object.raw_text
            paragraph_dict['paragraph_prepro'] = paragraph_object.preprocessed_text
            paragraph_dict['line_count'] = paragraph_object.line_count
            paragraph_dict['lines'] = list()

            for (line_number, line_object) in paragraph_object.numbered_line_objects:
                line_dict = dict()
                line_dict['line_number'] = line_number
                line_dict['line_id'] = f'P{index}_L{line_number}'
                line_dict['line_raw'] = line_object.raw_text
                line_dict['line_prepro'] = line_object.preprocessed_text
                line_dict['jisho_parse_html'] = line_object.jisho_parse_html
                line_dict['line_tl_deepl'] = line_object.tl_deepl
                line_dict['line_tl_google'] = line_object.tl_google
                line_dict['is_single_clause'] = line_object.is_single_clause()
                rekai_tts_output_list.append({line_object.raw_text: line_object.tts_b64_str})
                line_dict['clauses'] = list() if not line_object.is_single_clause() else None

                if not line_object.is_single_clause():
                    for (clause_number, clause_object) in line_object.numbered_clause_objects:
                        clause_dict = dict()
                        clause_dict['clause_id'] = f'P{index}_L{line_number}_C{clause_number}'
                        clause_dict['clause_raw'] = clause_object.raw_text
                        clause_dict['clause_prepro'] = clause_object.preprocessed_text
                        clause_dict['clause_tl_deepl'] = clause_object.tl_deepl
                        clause_dict['clause_tl_google'] = clause_object.tl_google
                        line_dict['clauses'].append(clause_dict)

                paragraph_dict['lines'].append(line_dict)

            rekai_output_dict['paragraphs'].append(paragraph_dict)

        output_json_string = json.dumps(rekai_output_dict, ensure_ascii=False)
        output_tts_json_string = json.dumps(rekai_tts_output_list, ensure_ascii=False)

        return output_json_string, output_tts_json_string




