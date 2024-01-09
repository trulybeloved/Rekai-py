
@staticmethod
def rekai_html(input_rekai_text_object: RekaiText):

    copy_button_content = '''<span style="font-size: .875em; margin-right: .125em; position: relative; top: -.25em; left: -.125em">📄<span style="position: absolute; top: .25em; left: .25em">📄</span></span>Raw'''
    audio_button_content = '''▶ TTS'''


    if input_rekai_text_object.text_header != '':
        html_title = input_rekai_text_object.text_header
    else:
        html_title = 'RekaiHTML'

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

    html_body_prefix = f'''<body><main><div id="primary" class="primary">'''
    html_body_suffix = f'''
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
    </html>'''


    html_body_main = '<div id="card-coloumn" class="card-coloumn">'

    for (paragraph_number, paragraph_object) in input_rekai_text_object.list_of_paragraph_object_tuples:

        paragraph_id = f'P{paragraph_number}'
        paragraph_raw = paragraph_object.paragraph_raw

        if paragraph_object.unparsable:
            # CARD MASTER START
            html_body_main += f'''<div id="{paragraph_id}" class="line-card-master">'''
            # CARD MASTER HEADER
            html_body_main += f'''
                   <div class="card-header">
                       <div class="card-header-left-half">
                           <p class="card-para-number">{paragraph_number}</p>
                           <p class="card-para-type">{paragraph_object.paragraph_type}</p>
                       </div>
                       <div class="card-header-right-half">
                           <!-- Specific ID and spedific argument to be passed into the function -->
                           <!-- function copyTextByElementId (elementId, buttonId) -->
                           <button id="{paragraph_id}-copy-button" class="raw-copy-button raw-para-copy-button"
                               onclick="copyTextByElementId('{paragraph_id}-raw-text', '{paragraph_id}-copy-button')">{copy_button_content}</button>
                       </div>
                   </div>'''
            # CARD MASTER CONTENTS
            html_body_main += f'''
            <div class="card-contents-raw master-raw">
                <!-- Specific ID -->
                <div id="{paragraph_id}-raw-text" class="card-contents-raw-text">
                <span class="japanese-raw-para">{paragraph_raw}</span>
                </div>
            </div>
            '''







    # CARD MASTER START
    html_body_main += f'''<div id="{paragraph_id}" class="line-card-master">'''
    # CARD MASTER HEADER
    html_body_main += f'''
    <div class="card-header">
        <div class="card-header-left-half">
            <p class="card-para-number">{paragraph_number}</p>
            <p class="card-para-type">Narration</p>
        </div>
        <div class="card-header-right-half">
            <!-- Specific ID and spedific argument to be passed into the function -->
            <!-- function copyTextByElementId (elementId, buttonId) -->
            <button id="{paragraph_id}-copy-button" class="raw-copy-button raw-para-copy-button"
                onclick="copyTextByElementId('{paragraph_id}-raw-text', '{paragraph_id}-copy-button')">{copy_button_content}</button>
        </div>
    </div>'''
    # CARD MASTER CONTENTS
    html_body_main += f'''
    <div class="card-contents-raw master-raw">
        <!-- Specific ID -->
        <div id="{paragraph_id}-raw-text" class="card-contents-raw-text">
        <span class="japanese-raw-para">{paragraph_raw}</span>
        </div>
    </div>
    '''
    # CARD SLAVE START
    html_body_main += f'''
    <!-- Specific ID -->
    <div id="{line_id}" class="line-card-slave">'''

    # CARD SLAVE HEADER
    html_body_main += f'''
        <div class="card-header">
            <div class="card-header-left-half">
                <!-- Specific Text Content -->
                <p class="card-line-number">{line_number}</p>
            </div>

            <div class="card-header-right-half">
                <!-- Specific ID and spedific argument to be passed into the function -->
                <!-- function copyTextByElementId (elementId, buttonId) -->
                <button id="{line_id}-copy-button" class="raw-copy-button raw-line-copy-button"
                    onclick="copyTextByElementId('{line_id}-raw-text', '{line_id}-copy-button')">{copy_button_content}</button>
                <!-- Specific ID -->
                <audioButton id="{line_id}-tts-button" class="audioButton audioButton-play">{audio_button_content}
                </audioButton>
                <!-- Specific ID and SRC -->
                <audio id="{line_id}-audioPlayer" class="audioPlayer"
                    src="{line_tts_path}"></audio>
            </div>
        </div>
    '''

    # CARD SLAVE CONTENTS
    # CARD SLAVE RAW
    html_body_main += f'''
        <div class="card-contents-raw slave-raw">
            <!-- Specific ID -->
            <div id="{line_id}-raw-text" class="card-contents-raw-text">
            <span class="japanese-raw-line">{line_raw}</span>
            </div>
        </div>
    '''

    # CARD SLAVE JISHO PARSE
    html_body_main += f'''
        <div id="para-1-line-1-jisho-parse" class="card-contents-jisho-parse">
            <div class="card-contents-jisho-parse-text">
            {jisho_parsed_html}
            </div>
        </div>        
    '''

    # CARD SLAVE END
    html_body_main += f'''
    </div>'''

    # CARD MASTER END
    html_body_main += f'</div>'


    # html_body_main += f''
    # html_body_main += f''
    # html_body_main += f''
    # html_body_main += f''
    # html_body_main += f''
    # html_body_main += f''
    # html_body_main += f''
    # html_body_main += f''
    # html_body_main += f''
    # html_body_main += f''
    # html_body_main += f''

