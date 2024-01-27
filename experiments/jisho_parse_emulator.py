from Rekai.nlp_modules.japanese_nlp import Parser, Classifier, Extractor
import pykakasi

# JISHO IS MORE ACCURATE. Sudachi has it's problems.
# Need to give the whole word to KAKASI for accurate

target_html = '''<section id="zen_bar" class="japanese_gothic focus" lang="ja">
                                    <ul class="clearfix">
                                        <li class="clearfix japanese_word" data-pos="Noun" title="Noun"
                                            data-tooltip-direction="bottom" data-tooltip-color="black"
                                            data-tooltip-margin="10">
                                            <span class="japanese_word__furigana_wrapper"> <span
                                                    class="japanese_word__furigana" data-text="普段">ふだん</span> </span>
                                            <span class="japanese_word__text_wrapper">
                                                <a data-word="普段" class="jisho-link"
                                                    href="https://jisho.org/search/%E6%99%AE%E6%AE%B5"> <span
                                                        class="japanese_word__text_with_furigana">普段</span></a> </span>
                                        </li>
                                        <li class="clearfix japanese_word" data-pos="Particle" title="Particle"
                                            data-tooltip-direction="bottom" data-tooltip-color="black"
                                            data-tooltip-margin="10">
                                            <span class="japanese_word__furigana_wrapper"></span> <span
                                                class="japanese_word__text_wrapper"><a data-word="の" class="jisho-link"
                                                    href="https://jisho.org/search/%E3%81%AE">の</a></span>
                                        </li>
                                        <li class="clearfix japanese_word" data-pos="Noun" title="Noun"
                                            data-tooltip-direction="bottom" data-tooltip-color="black"
                                            data-tooltip-margin="10">
                                            <span class="japanese_word__furigana_wrapper"> <span
                                                    class="japanese_word__furigana" data-text="目覚">めざ</span><span
                                                    class="japanese_word__furigana japanese_word__furigana-invisible japanese_word__furigana-invisible__last"
                                                    data-text="">め</span> </span> <span
                                                class="japanese_word__text_wrapper">
                                                <a data-word="目覚め" class="jisho-link"
                                                    href="https://jisho.org/search/%E7%9B%AE%E8%A6%9A%E3%82%81"> <span
                                                        class="japanese_word__text_with_furigana">目覚</span><span
                                                        class="japanese_word__text_without_furigana">め</span></a>
                                            </span>
                                        </li>
                                        <li class="clearfix japanese_word" data-pos="Particle" title="Particle"
                                            data-tooltip-direction="bottom" data-tooltip-color="black"
                                            data-tooltip-margin="10">
                                            <span class="japanese_word__furigana_wrapper"></span> <span
                                                class="japanese_word__text_wrapper"><a data-word="と" class="jisho-link"
                                                    href="https://jisho.org/search/%E3%81%A8">と</a></span>
                                        </li>
                                        <li class="clearfix japanese_word" data-pos="Verb" title="Verb"
                                            data-tooltip-direction="bottom" data-tooltip-color="black"
                                            data-tooltip-margin="10">
                                            <span class="japanese_word__furigana_wrapper"> <span
                                                    class="japanese_word__furigana" data-text="違">ちが</span><span
                                                    class="japanese_word__furigana japanese_word__furigana-invisible japanese_word__furigana-invisible__last"
                                                    data-text="">う</span> </span> <span
                                                class="japanese_word__text_wrapper">
                                                <a data-word="違う" class="jisho-link"
                                                    href="https://jisho.org/search/%E9%81%95%E3%81%86"> <span
                                                        class="japanese_word__text_with_furigana">違</span><span
                                                        class="japanese_word__text_without_furigana">う</span></a>
                                            </span>
                                        </li>
                                        <li class="clearfix japanese_word" data-pos="Noun" title="Noun"
                                            data-tooltip-direction="bottom" data-tooltip-color="black"
                                            data-tooltip-margin="10">
                                            <span class="japanese_word__furigana_wrapper"> <span
                                                    class="japanese_word__furigana" data-text="感触">かんしょく</span> </span>
                                            <span class="japanese_word__text_wrapper"> <a data-word="感触"
                                                    class="jisho-link"
                                                    href="https://jisho.org/search/%E6%84%9F%E8%A7%A6"> <span
                                                        class="japanese_word__text_with_furigana">感触</span></a> </span>
                                        </li>
                                        <li class="clearfix japanese_word" data-pos="Particle" title="Particle"
                                            data-tooltip-direction="bottom" data-tooltip-color="black"
                                            data-tooltip-margin="10">
                                            <span class="japanese_word__furigana_wrapper"></span> <span
                                                class="japanese_word__text_wrapper"><a data-word="は" class="jisho-link"
                                                    href="https://jisho.org/search/%E3%81%AF">は</a></span>
                                        </li>
                                        <li class="clearfix japanese_word"> <span
                                                class="japanese_word__furigana_wrapper"></span> <span
                                                class="japanese_word__text_wrapper">、</span> </li>
                                        <li class="clearfix japanese_word" data-pos="Pronoun" title="Pronoun"
                                            data-tooltip-direction="bottom" data-tooltip-color="black"
                                            data-tooltip-margin="10">
                                            <span class="japanese_word__furigana_wrapper"> <span
                                                    class="japanese_word__furigana" data-text="何">なに</span> </span>
                                            <span class="japanese_word__text_wrapper">
                                                <a data-word="何" class="jisho-link"
                                                    href="https://jisho.org/search/%E4%BD%95">
                                                    <span class="japanese_word__text_with_furigana">何</span></a> </span>
                                        </li>
                                        <li class="clearfix japanese_word" data-pos="Particle" title="Particle"
                                            data-tooltip-direction="bottom" data-tooltip-color="black"
                                            data-tooltip-margin="10">
                                            <span class="japanese_word__furigana_wrapper"></span> <span
                                                class="japanese_word__text_wrapper"><a data-word="も" class="jisho-link"
                                                    href="https://jisho.org/search/%E3%82%82">も</a></span>
                                        </li>
                                        <li class="clearfix japanese_word" data-pos="Noun" title="Noun"
                                            data-tooltip-direction="bottom" data-tooltip-color="black"
                                            data-tooltip-margin="10">
                                            <span class="japanese_word__furigana_wrapper"> <span
                                                    class="japanese_word__furigana" data-text="枕">まくら</span> </span>
                                            <span class="japanese_word__text_wrapper">
                                                <a data-word="枕" class="jisho-link"
                                                    href="https://jisho.org/search/%E6%9E%95">
                                                    <span class="japanese_word__text_with_furigana">枕</span></a> </span>
                                        </li>
                                        <li class="clearfix japanese_word" data-pos="Particle" title="Particle"
                                            data-tooltip-direction="bottom" data-tooltip-color="black"
                                            data-tooltip-margin="10">
                                            <span class="japanese_word__furigana_wrapper"></span> <span
                                                class="japanese_word__text_wrapper"><a data-word="に" class="jisho-link"
                                                    href="https://jisho.org/search/%E3%81%AB">に</a></span>
                                        </li>
                                        <li class="clearfix japanese_word" data-pos="Verb" title="Verb"
                                            data-tooltip-direction="bottom" data-tooltip-color="black"
                                            data-tooltip-margin="10">
                                            <span class="japanese_word__furigana_wrapper"> <span
                                                    class="japanese_word__furigana" data-text="限">かぎ</span><span
                                                    class="japanese_word__furigana japanese_word__furigana-invisible japanese_word__furigana-invisible__last"
                                                    data-text="">った</span> </span> <span
                                                class="japanese_word__text_wrapper"> <a data-word="限った"
                                                    class="jisho-link"
                                                    href="https://jisho.org/search/%E9%99%90%E3%81%A3%E3%81%9F"> <span
                                                        class="japanese_word__text_with_furigana">限</span><span
                                                        class="japanese_word__text_without_furigana">った</span></a>
                                            </span>
                                        </li>
                                        <li class="clearfix japanese_word" data-pos="Noun" title="Noun"
                                            data-tooltip-direction="bottom" data-tooltip-color="black"
                                            data-tooltip-margin="10">
                                            <span class="japanese_word__furigana_wrapper"> <span
                                                    class="japanese_word__furigana" data-text="話">はなし</span> </span>
                                            <span class="japanese_word__text_wrapper">
                                                <a data-word="話" class="jisho-link"
                                                    href="https://jisho.org/search/%E8%A9%B1">
                                                    <span class="japanese_word__text_with_furigana">話</span></a> </span>
                                        </li>
                                        <li class="clearfix japanese_word" data-pos="Particle" title="Particle"
                                            data-tooltip-direction="bottom" data-tooltip-color="black"
                                            data-tooltip-margin="10">
                                            <span class="japanese_word__furigana_wrapper"></span> <span
                                                class="japanese_word__text_wrapper"><a data-word="じゃない"
                                                    class="jisho-link"
                                                    href="https://jisho.org/search/%E3%81%98%E3%82%83%E3%81%AA%E3%81%84">じゃない</a></span>
                                        </li>
                                        <li class="clearfix japanese_word"> <span
                                                class="japanese_word__furigana_wrapper"></span> <span
                                                class="japanese_word__text_wrapper">。</span> </li>
                                    </ul>

                                </section>'''

list_of_word_pos_tuples = Parser.get_word_pos_from_jisho_html(target_html)
# print(list_of_word_pos_tuples)
sentence = ""


for (word, pos) in list_of_word_pos_tuples:

    sentence += word

print(sentence)

def get_furigana(input_text):
    transmuter = pykakasi.Kakasi()
    transmuted_results = transmuter.convert(input_text)
    print(transmuted_results)
    for item in transmuted_results:
        return f'{item["hira"]}'

get_furigana('普段')
def jisho_emulate(input_text):
    list_of_word_pos_tuples = Parser.tag_pos_sudachi(input_text)
    print(list_of_word_pos_tuples)
    jisho_search_url_prefix = 'https://jisho.org/search/'
    non_symbolic_pos = ["Noun", "Verb", "Adjective", "Adverb", "Conjunction", "Particle", "Auxiliary verb",
                        "Interjection", "Adnominal", "Pronoun", "Filler", "Unknown", "Na-adjective"
                        ]

    emulated_html_code = ''
    #Start of <section>
    html_start = '<section id="zen_bar" class="japanese_gothic focus" lang="ja"><ul class="clearfix">\n'
    emulated_html_code += html_start

    for (word, pos) in list_of_word_pos_tuples:
        #case for the word being completely kanji, or a combination of kanji and hiragana
        if not Classifier.contains_no_kanji(word) and pos in non_symbolic_pos:
            # Start of <li>
            emulated_html_code += f'<li class="clearfix japanese_word" data-pos="{pos}" title="{pos}" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">'

            kanji_block, non_kanji_block = Extractor.extract_kanji_block(word)
            furigana = get_furigana(kanji_block)

            emulated_html_code += f'<span class="japanese_word__furigana_wrapper"> <span class="japanese_word__furigana" data-text="{kanji_block}">{furigana}</span>'
            if non_kanji_block is not '':
                emulated_html_code += f'<span class="japanese_word__furigana japanese_word__furigana-invisible japanese_word__furigana-invisible__last" data-text="">{non_kanji_block}</span>'
            emulated_html_code += f'</span>' # closes out span of furigana wrapper class

            #japanese word text wrapper
            emulated_html_code += f'<span class="japanese_word__text_wrapper"> '
            emulated_html_code += f'<a data-word="{word}" class="jisho-link" href="{jisho_search_url_prefix}{word}">'
            emulated_html_code += f'<span class="japanese_word__text_with_furigana">{kanji_block}</span>'
            if non_kanji_block is not '':
                emulated_html_code += f'<span class="japanese_word__text_without_furigana">{non_kanji_block}</span>'
            emulated_html_code += f'</a></span>' # closes out span, a and li
            emulated_html_code += '</li>\n'

        #case for the word being completely hiragana or katakana without kanji
        if Classifier.contains_no_kanji(word) and pos in non_symbolic_pos:
            emulated_html_code += f'<li class="clearfix japanese_word" data-pos="{pos}" title="{pos}" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">'
            emulated_html_code += f'<span class="japanese_word__furigana_wrapper"></span>'
            emulated_html_code += f'<span class="japanese_word__text_wrapper"><a data-word="{word}" class="jisho-link" href="{jisho_search_url_prefix}{word}">{word}</a></span>'
            emulated_html_code += f'</li>\n'

        if Classifier.contains_no_kanji(word) and pos not in non_symbolic_pos : #need to make this better, check for both kanji and kana before excluding
            emulated_html_code += f'<li class="clearfix japanese_word"><span class="japanese_word__furigana_wrapper"> </span><span class="japanese_word__text_wrapper">{word}</span></li>\n'

    emulated_html_code += '</ul>'
    emulated_html_code += '</section>'

    return emulated_html_code



print(jisho_emulate(sentence))