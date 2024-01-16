import os.path
import shutil

from loguru import logger
from bs4 import BeautifulSoup
import minify_html

from custom_dataclasses import RekaiText, Paragraph, Line
from appconfig import AppConfig, RunConfig
from fetchers import Fetch


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

class GenerateHtml:
    class Config:
        pass

    class CommonElements:

        copy_button_content = '''<span style="font-size: .875em; margin-right: .125em; position: relative; top: -.25em; left: -.125em">📄<span style="position: absolute; top: .25em; left: .25em">📄</span></span>Raw'''
        audio_button_content = '''▶ TTS'''

    class FileOutput:

        @staticmethod
        def tts(line_id: str, line_raw: str, output_directory: str) -> str:
            tts_file_extension = AppConfig.tts_file_extension
            tts_bytes = Fetch.tts_bytes(raw_line=line_raw)
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

        def __init__(self, run_config_object: RunConfig):
            self.set_config(run_config_object=run_config_object)

        def set_config(self, run_config_object: RunConfig):
            self.config_preprocess = run_config_object.preprocess
            self.config_include_jisho_parse = run_config_object.run_jisho_parse
            self.config_include_tts = run_config_object.run_tts

        # Inner Elements ===========================================
        @staticmethod
        def audio_button(line_id: str, line_raw: str, output_directory: str) -> str:

            tts_file_output_folder_name = AppConfig.tts_output_folder_name
            tts_file_output_directory_path = os.path.join(output_directory, tts_file_output_folder_name)
            tts_file_name = GenerateHtml.FileOutput.tts(line_id=line_id, line_raw=line_raw,
                                                        output_directory=tts_file_output_directory_path)
            line_tts_relative_path = f'{tts_file_output_folder_name}/{tts_file_name}'

            output_html = f'''
            <audioButton id="{line_id}-tts-button" class="audioButton audioButton-play">{GenerateHtml.CommonElements.audio_button_content}
            </audioButton>
            <audio id="{line_id}-audioPlayer" class="audioPlayer"
                src="{line_tts_relative_path}"></audio>
            '''
            return output_html

        # Card Blocks ==============================================
        def para_card_unparsable(self, paragraph_number: int, input_rekai_paragraph_object: Paragraph) -> str:

            paragraph_object = input_rekai_paragraph_object
            paragraph_id = f'P{paragraph_number}'
            paragraph_raw = paragraph_object.raw_text

            # CARD MASTER START
            output_html = f'<div id="{paragraph_id}" class="line-card-master">'

            # CARD MASTER HEADER
            output_html += f''' 
               <div class="card-header">
                   <div class="card-header-left-half">
                       <div class="card-para-number"><span>{paragraph_number}</span></div>
                       <div class="card-para-type"><span>{paragraph_object.paragraph_type}</span></div>
                   </div>
                   <div class="card-header-right-half">
                       <button id="{paragraph_id}-copy-button" class="raw-copy-button raw-para-copy-button"
                           onclick="copyTextByElementId('{paragraph_id}-raw-text', '{paragraph_id}-copy-button')">{GenerateHtml.CommonElements.copy_button_content}</button>
                   </div>
               </div>'''

            # CARD MASTER CONTENTS
            output_html += f'''
                <div class="card-contents-raw master-raw">
                    <div id="{paragraph_id}-raw-text" class="card-contents-raw-text">
                    <span class="japanese-raw-para">{paragraph_raw}</span>
                    </div>
                </div>'''

            # CARD MASTER END
            output_html += f'</div>'

            return output_html

        def line_card(self, paragraph_number: int, line_number: int, input_rekai_line_object: Line,
                      output_directory: str) -> str:

            line_object = input_rekai_line_object
            line_id = f'P{paragraph_number}_L{line_number}'
            line_raw = line_object.raw_text

            if self.config_include_tts:
                audio_button_html = GenerateHtml.RekaiHtmlBlock.audio_button(line_id=line_id, line_raw=line_raw,
                                                                             output_directory=output_directory)
            else:
                audio_button_html = ''

            jisho_parsed_html = Fetch.jisho_parsed_html(raw_line=line_raw)

            # CARD SLAVE START
            output_html = f'<div id="{line_id}" class="line-card-slave collapsed">'

            # CARD SLAVE HEADER
            output_html += f'''
                <div class="card-header">
                    <div class="card-header-left-half">
                        <p class="card-line-number">{line_number}</p>
                    </div>

                    <div class="card-header-right-half">
                        <button id="{line_id}-copy-button" class="raw-copy-button raw-line-copy-button"
                            onclick="copyTextByElementId('{line_id}-raw-text', '{line_id}-copy-button')">{GenerateHtml.CommonElements.copy_button_content}</button>
                        {audio_button_html}
                    </div>
                </div>
            '''

            # CARD SLAVE CONTENTS
            # CARD SLAVE RAW
            output_html += f'''
                <div class="card-contents-raw slave-raw">
                    <div id="{line_id}-raw-text" class="card-contents-raw-text">
                    <span class="japanese-raw-line">{line_raw}</span>
                    </div>
                </div>
            '''

            # CARD SLAVE JISHO PARSE
            output_html += f'''
                <div id="{line_id}-jisho-parse" class="card-contents-jisho-parse">
                    <div class="card-contents-jisho-parse-text">
                    {jisho_parsed_html}
                    </div>
                </div>        
            '''

            # CARD SLAVE END
            output_html += f'''
            </div>'''

            return output_html

        def para_card(self, paragraph_number: int, input_rekai_paragraph_object: Paragraph,
                      output_directory: str) -> str:

            paragraph_object = input_rekai_paragraph_object
            paragraph_id = f'P{paragraph_number}'
            paragraph_raw = paragraph_object.raw_text

            # CARD MASTER START
            output_html = f'<div id="{paragraph_id}" class="line-card-master">'

            # CARD MASTER HEADER
            output_html += f''' 
               <div class="card-header">
                   <div class="card-header-left-half">
                       <div class="card-para-number"><span>{paragraph_number}</span></div>
                       <div class="card-para-type"><span>{paragraph_object.paragraph_type}</span></div>
                       <div class="expand-collapse-button" onclick="expandCollapseCard('{paragraph_id}')">Expand</div>
                   </div>
                   <div class="card-header-right-half">
                       <button id="{paragraph_id}-copy-button" class="raw-copy-button raw-para-copy-button"
                           onclick="copyTextByElementId('{paragraph_id}-raw-text', '{paragraph_id}-copy-button')">{GenerateHtml.CommonElements.copy_button_content}</button>
                   </div>
               </div>'''

            # CARD MASTER CONTENTS
            output_html += f'''
                <div class="card-contents-raw master-raw">
                    <div id="{paragraph_id}-raw-text" class="card-contents-raw-text">
                    <span class="japanese-raw-para">{paragraph_raw}</span>
                    </div>
                </div>'''

            # GENERATE SLAVE CARDS
            for (line_number, line_object) in input_rekai_paragraph_object.numbered_line_objects:
                output_html += f'{self.line_card(paragraph_number=paragraph_number, line_number=line_number, input_rekai_line_object=line_object, output_directory=output_directory)}'

            # CARD MASTER END
            output_html += f'</div>'

            return output_html

        # Page Blocks ==============================================
        def html_head(self, html_title: str) -> str:
            html_head = f'''
            <!DOCTYPE html>
            <html>

            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{html_title}</title>

                <link rel="stylesheet" href="css/styles.css">
                <link rel="preconnect" href="https://fonts.googleapis.com">
                <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                <link rel="stylesheet"
                    href="https://fonts.googleapis.com/css2?family=Roboto:wght@100;300;400;500;700;900&display=swap">
            </head>
            '''
            return html_head

        def html_body_prefix(self, ) -> str:
            output_html = f'''<body><main><div id="primary" class="primary">'''
            return output_html

        def html_body_main(self, input_rekai_text_object: RekaiText, output_directory: str) -> str:

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

        def html_body_suffix(self) -> str:
            output_html = f'''
                     <!-- SIDEBAR --------------------------------------------------------------------->
                        <div id="sidebar-placeholder" class="sidebar-placeholder">
                            <div id="right-sidebar" class="right-sidebar sidebar-expanded">
                            <div class="right-sidebar-iframe">
                                <iframe id="sidebar-iframe" class="sidebar-iframe" name="sidebar-iframe" width="100%" height="100%"
                                    src="https://jisho.org/" frameborder="0"></iframe>
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
                                <div>Arc 8 - C 25</div>
                            </div>
                        </div>
                        <div class="top-bar-mid-section">
                            <!-- function toggleElementDisplay(buttonId, elementClass, displayType, showText, hideText) -->
                            <button id="toggle-raw-para-button" class="top-bar-button top-bar-button-generic"
                                onclick="toggleElementDisplay('toggle-raw-para-button','.card-contents-raw.master-raw','flex', 'Show RAW Para', 'Hide RAW Para')">Hide
                                RAW Para</button>
                            <button id="toggle-jisho-button" class="top-bar-button top-bar-button-generic"
                                onclick="toggleElementDisplay('toggle-jisho-button','.card-contents-jisho-parse','flex', 'Show JishoParse', 'Hide JishoParse')">Hide
                                JishoParse</button>
                            <button id="toggle-inner-raw-button" class="top-bar-button top-bar-button-generic" onclick="toggleElementDisplay('toggle-inner-raw-button', '.japanese-raw-line', 'block', 'Show Inner Raw', 'Hide Inner Raw')">ToggleInnerRAw</button>
                            <button class="top-bar-button top-bar-button-generic">Button</button>
                        </div>
                        <div class="top-bar-end-section">
                            <button id="toggle-light-dark-mode-button" class="top-bar-button top-bar-button-generic" onclick="toggleDarkMode()">Light|Dark</button>
                            <button id="toggle-sidebar-button" class="top-bar-button top-bar-button-generic" onclick="toggleRightSidebar()">Hide Sidebar</button>
                        </div>
                    </div>
                </div>

                <!-- SCRIPT --------------------------------------------------------------------->
                <script src="javascript/rekai.js"></script>
            </body>
            </html>
            '''
            return output_html

    class RekaiHtml:
        @staticmethod
        def full_html(run_config_object: RunConfig, html_title: str, input_rekai_text_object: RekaiText,
                      output_directory: str, post_process: str = 'minify') -> None:

            GenerateHtml.FileOutput.associated_files(output_directory=output_directory)

            generate = GenerateHtml.RekaiHtmlBlock(run_config_object=run_config_object)

            html = generate.html_head(html_title=html_title)
            html += generate.html_body_prefix()
            html += generate.html_body_main(input_rekai_text_object=input_rekai_text_object,
                                            output_directory=output_directory)
            html += generate.html_body_suffix()

            if post_process == 'prettify':
                html = HtmlUtilities.prettify_html(html)
            elif post_process == 'minify':
                html = HtmlUtilities.minify(html)

            output_html_file_path = os.path.join(output_directory, 'rekai.html')

            with open(output_html_file_path, 'w', encoding='utf-8') as rekai_html_file:
                rekai_html_file.write(html)

            os.startfile(output_html_file_path)

            logger.info('RekaiHTML file generated sucessfully')
