import os.path
import shutil
from loguru import logger
from bs4 import BeautifulSoup

from Rekai.custom_dataclasses import RekaiText, Paragraph, Line
from Rekai.appconfig import AppConfig
from Rekai.fetchers import Fetch


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

        # Inner Elements ===========================================
        @staticmethod
        def audio_button(line_id: str, line_raw: str, output_directory: str) -> str:

            tts_file_output_folder_name = AppConfig.tts_output_folder_name
            tts_file_output_directory_path = os.path.join(output_directory, tts_file_output_folder_name)
            tts_file_name = GenerateHtml.FileOutput.tts(line_id=line_id, line_raw=line_raw, output_directory=tts_file_output_directory_path)
            line_tts_relative_path = f'{tts_file_output_folder_name}/{tts_file_name}'

            output_html = f'''
            <audioButton id="{line_id}-tts-button" class="audioButton audioButton-play">{GenerateHtml.CommonElements.audio_button_content}
            </audioButton>
            <audio id="{line_id}-audioPlayer" class="audioPlayer"
                src="{line_tts_relative_path}"></audio>
            '''
            return output_html

        # Card Blocks ==============================================
        @staticmethod
        def para_card_unparsable(paragraph_number: int, input_rekai_paragraph_object: Paragraph) -> str:

            paragraph_object = input_rekai_paragraph_object
            paragraph_id = f'P{paragraph_number}'
            paragraph_raw = paragraph_object.paragraph_raw

            # CARD MASTER START
            output_html = f'<div id="{paragraph_id}" class="line-card-master">'

            # CARD MASTER HEADER
            output_html += f''' 
               <div class="card-header">
                   <div class="card-header-left-half">
                       <p class="card-para-number">{paragraph_number}</p>
                       <p class="card-para-type">{paragraph_object.paragraph_type}</p>
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

        @staticmethod
        def line_card(paragraph_number: int, line_number: int, input_rekai_line_object: Line, output_directory: str) -> str:

            line_object = input_rekai_line_object
            line_id = f'P{paragraph_number}_L{line_number}'
            line_raw = line_object.line_raw

            audio_button_html = GenerateHtml.RekaiHtmlBlock.audio_button(line_id=line_id, line_raw=line_raw, output_directory=output_directory)
            jisho_parsed_html = Fetch.jisho_parsed_html(raw_line=line_raw)


            # CARD SLAVE START
            output_html = f'<div id="{line_id}" class="line-card-slave">'

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

        @staticmethod
        def para_card(paragraph_number: int, input_rekai_paragraph_object: Paragraph, output_directory: str) -> str:

            paragraph_object = input_rekai_paragraph_object
            paragraph_id = f'P{paragraph_number}'
            paragraph_raw = paragraph_object.paragraph_raw

            # CARD MASTER START
            output_html = f'<div id="{paragraph_id}" class="line-card-master">'

            # CARD MASTER HEADER
            output_html += f''' 
               <div class="card-header">
                   <div class="card-header-left-half">
                       <p class="card-para-number">{paragraph_number}</p>
                       <p class="card-para-type">{paragraph_object.paragraph_type}</p>
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
            for (line_number, line_object) in input_rekai_paragraph_object.list_of_line_object_tuples:
                output_html += f'{GenerateHtml.RekaiHtmlBlock.line_card(paragraph_number=paragraph_number, line_number=line_number, input_rekai_line_object=line_object, output_directory=output_directory)}'

            # CARD MASTER END
            output_html += f'</div>'

            return output_html

        # Page Blocks ==============================================
        @staticmethod
        def html_head(html_title: str) -> str:
            html_head = f'''
            <!DOCTYPE html>
            <html>

            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{html_title}</title>

                <link rel="stylesheet" href="css/jishoparse.css">
                <link rel="stylesheet" href="css/styles.css">
                <link rel="preconnect" href="https://fonts.googleapis.com">
                <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
                <link rel="stylesheet"
                    href="https://fonts.googleapis.com/css2?family=Roboto:wght@100;300;400;500;700;900&display=swap">
            </head>
            '''
            return html_head

        @staticmethod
        def html_body_prefix() -> str:
            output_html = f'''<body><main><div id="primary" class="primary">'''
            return output_html

        @staticmethod
        def html_body_main(input_rekai_text_object: RekaiText, output_directory: str) -> str:

            output_html = '<div id="card-coloumn" class="card-coloumn">'

            for (index, paragraph_object) in input_rekai_text_object.list_of_paragraph_object_tuples:
                if paragraph_object.unparsable:
                    output_html += GenerateHtml.RekaiHtmlBlock.para_card_unparsable(
                        input_rekai_paragraph_object=paragraph_object,
                        paragraph_number=index)
                else:
                    output_html += GenerateHtml.RekaiHtmlBlock.para_card(
                        input_rekai_paragraph_object=paragraph_object,
                        paragraph_number=index,
                        output_directory=output_directory)

            output_html += '</div>'

            return output_html

        @staticmethod
        def html_body_suffix() -> str:
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
                            <button id="toggle-sidebar-button" class="top-bar-button top-bar-button-generic"
                                onclick="toggleRightSidebar()">Hide Sidebar</button>
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
        def full_html(html_title: str, input_rekai_text_object: RekaiText, output_directory: str, prettify: bool = False) -> None:

            GenerateHtml.FileOutput.associated_files(output_directory=output_directory)

            html = GenerateHtml.RekaiHtmlBlock.html_head(html_title=html_title)
            html += GenerateHtml.RekaiHtmlBlock.html_body_prefix()
            html += GenerateHtml.RekaiHtmlBlock.html_body_main(input_rekai_text_object=input_rekai_text_object, output_directory=output_directory)
            html += GenerateHtml.RekaiHtmlBlock.html_body_suffix()

            if prettify:
                soup = BeautifulSoup(html, 'html.parser')
                html = soup.prettify()

            output_html_file_path = os.path.join(output_directory, 'rekai.html')

            with open(output_html_file_path, 'w', encoding='utf-8') as rekai_html_file:
                rekai_html_file.write(html)

            os.startfile(output_html_file_path)

            logger.info('RekaiHTML file generated sucessfully')


