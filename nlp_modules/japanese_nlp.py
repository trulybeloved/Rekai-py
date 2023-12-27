"""Functions related to japanese NLP"""

from html.parser import HTMLParser


from bs4 import BeautifulSoup
import re
import loguru
import string

import MeCab
from sudachipy import Dictionary
from Rekai.nlp_modules.basic_nlp import FundamentalPatterns
from Rekai.nlp_modules.regex import regex_for_any_single_kanji, regex_for_selecting_blocks_of_kanji



logger = loguru.logger

jisho_test_html = """<section id="zen_bar" class="japanese_gothic focus" lang="ja">      <ul class="clearfix">            <li class="clearfix japanese_word" data-pos="Noun" title="Noun" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper">                  <span class="japanese_word__furigana" data-text="普段">ふだん</span>                </span>                <span class="japanese_word__text_wrapper">                  <a data-word="普段" class="jisho-link" href="https://jisho.org/search/%E6%99%AE%E6%AE%B5">                    <span class="japanese_word__text_with_furigana">普段</span></a>                </span>            </li>            <li class="clearfix japanese_word" data-pos="Particle" title="Particle" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper"></span>                <span class="japanese_word__text_wrapper"><a data-word="の" class="jisho-link" href="https://jisho.org/search/%E3%81%AE">の</a></span>            </li>            <li class="clearfix japanese_word" data-pos="Noun" title="Noun" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper">                  <span class="japanese_word__furigana" data-text="目覚">めざ</span><span class="japanese_word__furigana japanese_word__furigana-invisible japanese_word__furigana-invisible__last" data-text="">め</span>                </span>                <span class="japanese_word__text_wrapper">                  <a data-word="目覚め" class="jisho-link" href="https://jisho.org/search/%E7%9B%AE%E8%A6%9A%E3%82%81">                    <span class="japanese_word__text_with_furigana">目覚</span><span class="japanese_word__text_without_furigana">め</span></a>                </span>            </li>            <li class="clearfix japanese_word" data-pos="Particle" title="Particle" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper"></span>                <span class="japanese_word__text_wrapper"><a data-word="と" class="jisho-link" href="https://jisho.org/search/%E3%81%A8">と</a></span>            </li>            <li class="clearfix japanese_word" data-pos="Verb" title="Verb" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper">                  <span class="japanese_word__furigana" data-text="違">ちが</span><span class="japanese_word__furigana japanese_word__furigana-invisible japanese_word__furigana-invisible__last" data-text="">う</span>                </span>                <span class="japanese_word__text_wrapper">                  <a data-word="違う" class="jisho-link" href="https://jisho.org/search/%E9%81%95%E3%81%86">                    <span class="japanese_word__text_with_furigana">違</span><span class="japanese_word__text_without_furigana">う</span></a>                </span>            </li>            <li class="clearfix japanese_word" data-pos="Noun" title="Noun" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper">                  <span class="japanese_word__furigana" data-text="感触">かんしょく</span>                </span>                <span class="japanese_word__text_wrapper">                  <a data-word="感触" class="jisho-link" href="https://jisho.org/search/%E6%84%9F%E8%A7%A6">                    <span class="japanese_word__text_with_furigana">感触</span></a>                </span>            </li>            <li class="clearfix japanese_word" data-pos="Particle" title="Particle" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper"></span>                <span class="japanese_word__text_wrapper"><a data-word="は" class="jisho-link" href="https://jisho.org/search/%E3%81%AF">は</a></span>            </li>            <li class="clearfix japanese_word">              <span class="japanese_word__furigana_wrapper"></span>              <span class="japanese_word__text_wrapper">、</span>            </li>            <li class="clearfix japanese_word" data-pos="Pronoun" title="Pronoun" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper">                  <span class="japanese_word__furigana" data-text="何">なに</span>                </span>                <span class="japanese_word__text_wrapper">                  <a data-word="何" class="jisho-link" href="https://jisho.org/search/%E4%BD%95">                    <span class="japanese_word__text_with_furigana">何</span></a>                </span>            </li>            <li class="clearfix japanese_word" data-pos="Particle" title="Particle" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper"></span>                <span class="japanese_word__text_wrapper"><a data-word="も" class="jisho-link" href="https://jisho.org/search/%E3%82%82">も</a></span>            </li>            <li class="clearfix japanese_word" data-pos="Noun" title="Noun" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper">                  <span class="japanese_word__furigana" data-text="枕">まくら</span>                </span>                <span class="japanese_word__text_wrapper">                  <a data-word="枕" class="jisho-link" href="https://jisho.org/search/%E6%9E%95">                    <span class="japanese_word__text_with_furigana">枕</span></a>                </span>            </li>            <li class="clearfix japanese_word" data-pos="Particle" title="Particle" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper"></span>                <span class="japanese_word__text_wrapper"><a data-word="に" class="jisho-link" href="https://jisho.org/search/%E3%81%AB">に</a></span>            </li>            <li class="clearfix japanese_word" data-pos="Verb" title="Verb" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper">                  <span class="japanese_word__furigana" data-text="限">かぎ</span><span class="japanese_word__furigana japanese_word__furigana-invisible japanese_word__furigana-invisible__last" data-text="">った</span>                </span>                <span class="japanese_word__text_wrapper">                  <a data-word="限った" class="jisho-link" href="https://jisho.org/search/%E9%99%90%E3%81%A3%E3%81%9F">                    <span class="japanese_word__text_with_furigana">限</span><span class="japanese_word__text_without_furigana">った</span></a>                </span>            </li>            <li class="clearfix japanese_word" data-pos="Noun" title="Noun" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper">                  <span class="japanese_word__furigana" data-text="話">はなし</span>                </span>                <span class="japanese_word__text_wrapper">                  <a data-word="話" class="jisho-link" href="https://jisho.org/search/%E8%A9%B1">                    <span class="japanese_word__text_with_furigana">話</span></a>                </span>            </li>            <li class="clearfix japanese_word" data-pos="Particle" title="Particle" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper"></span>                <span class="japanese_word__text_wrapper"><a data-word="じゃない" class="jisho-link" href="https://jisho.org/search/%E3%81%98%E3%82%83%E3%81%AA%E3%81%84">じゃない</a></span>            </li>            <li class="clearfix japanese_word">              <span class="japanese_word__furigana_wrapper"></span>              <span class="japanese_word__text_wrapper">。</span>            </li>            </ul><ul class="clearfix">            <li class="clearfix japanese_word" data-pos="Proper noun" title="Proper noun" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper"></span>                <span class="japanese_word__text_wrapper"><a data-word="スバル" class="jisho-link" href="https://jisho.org/search/%E3%82%B9%E3%83%90%E3%83%AB">スバル</a></span>            </li>            <li class="clearfix japanese_word" data-pos="Particle" title="Particle" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper"></span>                <span class="japanese_word__text_wrapper"><a data-word="の" class="jisho-link" href="https://jisho.org/search/%E3%81%AE">の</a></span>            </li>            <li class="clearfix japanese_word" data-pos="Noun" title="Noun" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper">                  <span class="japanese_word__furigana" data-text="日本人">にっぽんじん</span>                </span>                <span class="japanese_word__text_wrapper">                  <a data-word="日本人" class="jisho-link" href="https://jisho.org/search/%E6%97%A5%E6%9C%AC%E4%BA%BA">                    <span class="japanese_word__text_with_furigana">日本人</span></a>                </span>            </li>            <li class="clearfix japanese_word" data-pos="Noun" title="Noun" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper">                  <span class="japanese_word__furigana" data-text="女性">じょせい</span>                </span>                <span class="japanese_word__text_wrapper">                  <a data-word="女性" class="jisho-link" href="https://jisho.org/search/%E5%A5%B3%E6%80%A7">                    <span class="japanese_word__text_with_furigana">女性</span></a>                </span>            </li>            <li class="clearfix japanese_word" data-pos="Particle" title="Particle" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper"></span>                <span class="japanese_word__text_wrapper"><a data-word="の" class="jisho-link" href="https://jisho.org/search/%E3%81%AE">の</a></span>            </li>            <li class="clearfix japanese_word" data-pos="Noun" title="Noun" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper">                  <span class="japanese_word__furigana" data-text="平均身長">へいきんしんちょう</span>                </span>                <span class="japanese_word__text_wrapper">                  <a data-word="平均身長" class="jisho-link" href="https://jisho.org/search/%E5%B9%B3%E5%9D%87%E8%BA%AB%E9%95%B7">                    <span class="japanese_word__text_with_furigana">平均身長</span></a>                </span>            </li>            <li class="clearfix japanese_word" data-pos="Particle" title="Particle" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper"></span>                <span class="japanese_word__text_wrapper"><a data-word="より" class="jisho-link" href="https://jisho.org/search/%E3%82%88%E3%82%8A">より</a></span>            </li>            <li class="clearfix japanese_word" data-pos="Noun" title="Noun" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper">                  <span class="japanese_word__furigana japanese_word__furigana-invisible " data-text="ほんの">ほんの</span><span class="japanese_word__furigana" data-text="少">すこ</span><span class="japanese_word__furigana japanese_word__furigana-invisible japanese_word__furigana-invisible__last" data-text="">し</span>                </span>                <span class="japanese_word__text_wrapper">                  <a data-word="ほんの少し" class="jisho-link" href="https://jisho.org/search/%E3%81%BB%E3%82%93%E3%81%AE%E5%B0%91%E3%81%97">                    <span class="japanese_word__text_without_furigana">ほんの</span><span class="japanese_word__text_with_furigana">少</span><span class="japanese_word__text_without_furigana">し</span></a>                </span>            </li>            <li class="clearfix japanese_word" data-pos="Particle" title="Particle" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper"></span>                <span class="japanese_word__text_wrapper"><a data-word="だけ" class="jisho-link" href="https://jisho.org/search/%E3%81%A0%E3%81%91">だけ</a></span>            </li>            <li class="clearfix japanese_word" data-pos="Adjective" title="Adjective" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper">                  <span class="japanese_word__furigana" data-text="大">おお</span><span class="japanese_word__furigana japanese_word__furigana-invisible japanese_word__furigana-invisible__last" data-text="">きい</span>                </span>                <span class="japanese_word__text_wrapper">                  <a data-word="大きい" class="jisho-link" href="https://jisho.org/search/%E5%A4%A7%E3%81%8D%E3%81%84">                    <span class="japanese_word__text_with_furigana">大</span><span class="japanese_word__text_without_furigana">きい</span></a>                </span>            </li>            <li class="clearfix japanese_word" data-pos="Noun" title="Noun" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper">                  <span class="japanese_word__furigana" data-text="体">からだ</span>                </span>                <span class="japanese_word__text_wrapper">                  <a data-word="体" class="jisho-link" href="https://jisho.org/search/%E4%BD%93">                    <span class="japanese_word__text_with_furigana">体</span></a>                </span>            </li>            <li class="clearfix japanese_word">              <span class="japanese_word__furigana_wrapper"></span>              <span class="japanese_word__text_wrapper">、</span>            </li>            <li class="clearfix japanese_word" data-pos="Pronoun" title="Pronoun" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper"></span>                <span class="japanese_word__text_wrapper"><a data-word="それ" class="jisho-link" href="https://jisho.org/search/%E3%81%9D%E3%82%8C">それ</a></span>            </li>            <li class="clearfix japanese_word" data-pos="Particle" title="Particle" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper"></span>                <span class="japanese_word__text_wrapper"><a data-word="を" class="jisho-link" href="https://jisho.org/search/%E3%82%92">を</a></span>            </li>            <li class="clearfix japanese_word" data-pos="Verb" title="Verb" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper">                  <span class="japanese_word__furigana" data-text="受">う</span><span class="japanese_word__furigana japanese_word__furigana-invisible " data-text="け">け</span><span class="japanese_word__furigana" data-text="止">と</span><span class="japanese_word__furigana japanese_word__furigana-invisible japanese_word__furigana-invisible__last" data-text="">めている</span>                </span>                <span class="japanese_word__text_wrapper">                  <a data-word="受け止めている" class="jisho-link" href="https://jisho.org/search/%E5%8F%97%E3%81%91%E6%AD%A2%E3%82%81%E3%81%A6%E3%81%84%E3%82%8B">                    <span class="japanese_word__text_with_furigana">受</span><span class="japanese_word__text_without_furigana">け</span><span class="japanese_word__text_with_furigana">止</span><span class="japanese_word__text_without_furigana">めている</span></a>                </span>            </li>            <li class="clearfix japanese_word" data-pos="Noun" title="Noun" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper"></span>                <span class="japanese_word__text_wrapper"><a data-word="ベッド" class="jisho-link" href="https://jisho.org/search/%E3%83%99%E3%83%83%E3%83%89">ベッド</a></span>            </li>            <li class="clearfix japanese_word" data-pos="Particle" title="Particle" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper"></span>                <span class="japanese_word__text_wrapper"><a data-word="も" class="jisho-link" href="https://jisho.org/search/%E3%82%82">も</a></span>            </li>            <li class="clearfix japanese_word">              <span class="japanese_word__furigana_wrapper"></span>              <span class="japanese_word__text_wrapper">、</span>            </li>            <li class="clearfix japanese_word" data-pos="Noun" title="Noun" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper"></span>                <span class="japanese_word__text_wrapper"><a data-word="すべ" class="jisho-link" href="https://jisho.org/search/%E3%81%99%E3%81%B9">すべ</a></span>            </li>            <li class="clearfix japanese_word" data-pos="Noun" title="Noun" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper"></span>                <span class="japanese_word__text_wrapper"><a data-word="らか" class="jisho-link" href="https://jisho.org/search/%E3%82%89%E3%81%8B">らか</a></span>            </li>            <li class="clearfix japanese_word" data-pos="Particle" title="Particle" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper"></span>                <span class="japanese_word__text_wrapper"><a data-word="な" class="jisho-link" href="https://jisho.org/search/%E3%81%AA">な</a></span>            </li>            <li class="clearfix japanese_word" data-pos="Noun" title="Noun" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper">                  <span class="japanese_word__furigana" data-text="肌触">はだざわ</span><span class="japanese_word__furigana japanese_word__furigana-invisible japanese_word__furigana-invisible__last" data-text="">り</span>                </span>                <span class="japanese_word__text_wrapper">                  <a data-word="肌触り" class="jisho-link" href="https://jisho.org/search/%E8%82%8C%E8%A7%A6%E3%82%8A">                    <span class="japanese_word__text_with_furigana">肌触</span><span class="japanese_word__text_without_furigana">り</span></a>                </span>            </li>            <li class="clearfix japanese_word" data-pos="Particle" title="Particle" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper"></span>                <span class="japanese_word__text_wrapper"><a data-word="の" class="jisho-link" href="https://jisho.org/search/%E3%81%AE">の</a></span>            </li>            <li class="clearfix japanese_word" data-pos="Noun" title="Noun" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper"></span>                <span class="japanese_word__text_wrapper"><a data-word="シーツ" class="jisho-link" href="https://jisho.org/search/%E3%82%B7%E3%83%BC%E3%83%84">シーツ</a></span>            </li>            <li class="clearfix japanese_word" data-pos="Particle" title="Particle" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper"></span>                <span class="japanese_word__text_wrapper"><a data-word="も" class="jisho-link" href="https://jisho.org/search/%E3%82%82">も</a></span>            </li>            <li class="clearfix japanese_word">              <span class="japanese_word__furigana_wrapper"></span>              <span class="japanese_word__text_wrapper">、</span>            </li>            <li class="clearfix japanese_word" data-pos="Noun" title="Noun" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper">                  <span class="japanese_word__furigana" data-text="全部">ぜんぶ</span>                </span>                <span class="japanese_word__text_wrapper">                  <a data-word="全部" class="jisho-link" href="https://jisho.org/search/%E5%85%A8%E9%83%A8">                    <span class="japanese_word__text_with_furigana">全部</span></a>                </span>            </li>            <li class="clearfix japanese_word" data-pos="Particle" title="Particle" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper"></span>                <span class="japanese_word__text_wrapper"><a data-word="が" class="jisho-link" href="https://jisho.org/search/%E3%81%8C">が</a></span>            </li>            <li class="clearfix japanese_word" data-pos="Noun" title="Noun" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper">                  <span class="japanese_word__furigana" data-text="全部">ぜんぶ</span>                </span>                <span class="japanese_word__text_wrapper">                  <a data-word="全部" class="jisho-link" href="https://jisho.org/search/%E5%85%A8%E9%83%A8">                    <span class="japanese_word__text_with_furigana">全部</span></a>                </span>            </li>            <li class="clearfix japanese_word">              <span class="japanese_word__furigana_wrapper"></span>              <span class="japanese_word__text_wrapper">、</span>            </li>            <li class="clearfix japanese_word" data-pos="Adverb" title="Adverb" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper"></span>                <span class="japanese_word__text_wrapper"><a data-word="いつも" class="jisho-link" href="https://jisho.org/search/%E3%81%84%E3%81%A4%E3%82%82">いつも</a></span>            </li>            <li class="clearfix japanese_word" data-pos="Particle" title="Particle" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper"></span>                <span class="japanese_word__text_wrapper"><a data-word="と" class="jisho-link" href="https://jisho.org/search/%E3%81%A8">と</a></span>            </li>            <li class="clearfix japanese_word" data-pos="Verb" title="Verb" data-tooltip-direction="bottom" data-tooltip-color="black" data-tooltip-margin="10">                <span class="japanese_word__furigana_wrapper">                  <span class="japanese_word__furigana" data-text="違">ちが</span><span class="japanese_word__furigana japanese_word__furigana-invisible japanese_word__furigana-invisible__last" data-text="">いすぎていた</span>                </span>                <span class="japanese_word__text_wrapper">                  <a data-word="違いすぎていた" class="jisho-link" href="https://jisho.org/search/%E9%81%95%E3%81%84%E3%81%99%E3%81%8E%E3%81%A6%E3%81%84%E3%81%9F">                    <span class="japanese_word__text_with_furigana">違</span><span class="japanese_word__text_without_furigana">いすぎていた</span></a>                </span>            </li>            <li class="clearfix japanese_word">              <span class="japanese_word__furigana_wrapper"></span>              <span class="japanese_word__text_wrapper">。</span>            </li>            </ul><ul class="clearfix">      </ul>    </section>"""


test_text = """
――これは本気でマズイことになった。





　一文無しで途方に暮れながら、彼の心中はそんな一言で埋め尽くされていた。



「……」

「やっぱ、貨幣価値とかって全然違うんだよな……」



　群衆に紛れれば一瞬で見失いそうなほど凡庸な見た目だ。

　が、そんな彼を見る人々の視線には『珍奇』なものでも見るような不可解な色が濃い。
"""
test_tokeizer = 'が、そんな彼を見る人々の視線には『珍奇』なものでも見るような不可解な色が濃い。'

# class FundamentalPatterns:
#     """
#     Class of basic pattern recognition functions. Takes a string as input and returns a bool
#     """
#
#     @staticmethod
#     def contains_only_whitespace(input_text: str) -> bool:
#         set_of_whitespace_characters = set(string.whitespace)
#         return all(character in set_of_whitespace_characters for character in input_text)
#
#     @staticmethod
#     def contains_only_digits(input_text: str) -> bool:
#         set_of_digit_characters = set(string.digits)
#         return all(character in set_of_digit_characters for character in input_text)
#
#     @staticmethod
#     def contains_only_punctuation(input_text: str) -> bool:
#         set_of_punctuation_characters = set(string.punctuation)
#         return all(character in set_of_punctuation_characters for character in input_text)


class Classifier:

    @staticmethod
    def contains_no_parsable_text(input_text: str) -> bool:
        replacement_list = ["「", "」", "―", "！", "？", '『', '』']
        for char in replacement_list:
            input_text = input_text.replace(char, '')

        return len(input_text) < 3
    @staticmethod
    def contains_no_kanji(input_text: str) -> bool:
        regex_pattern_for_any_kanji = re.compile(regex_for_any_single_kanji, re.IGNORECASE)
        is_kanji_present = regex_pattern_for_any_kanji.search(input_text)
        if is_kanji_present:
            return False
        else:
            return True

    @staticmethod
    def extract_kanji_block(input_text: str) -> tuple[str, str]:
        regex_pattern_for_kanji_block = re.compile(regex_for_selecting_blocks_of_kanji)
        kanji_block_match = regex_pattern_for_kanji_block.match(input_text)
        kanji_block = kanji_block_match.group(0)
        non_kanji_block = input_text.replace(kanji_block, '')
        return kanji_block, non_kanji_block

# print(Classifier.contains_no_kanji('濃'))
# print(Classifier.contains_no_kanji('だ'))
# print(Classifier.extract_kanji_block('解な'))

class TextSplitter:

    @staticmethod
    def split_para_to_list_of_lines(input_text: str, *, strip_each_line: bool = True, trim_list: bool = True, delimiter: str = '。') -> list:

        list_of_lines = input_text.split(delimiter)



        if strip_each_line:
            list_of_lines = [line.strip() for line in list_of_lines]

        if trim_list:
            list_of_lines = [line for line in list_of_lines
                             if not FundamentalPatterns.contains_only_whitespace(line)]

        list_of_lines = [f'{line}{delimiter}' for line in list_of_lines]

        return list_of_lines

class Parser:
    @staticmethod
    def parse_html(html_code):
        # Parse the HTML code
        soup = BeautifulSoup(html_code, 'html.parser')

        # Find all <li> elements with class "japanese_word"
        japanese_word_elements = soup.find_all('li', class_='japanese_word')

        # Extract and return the values of data-pos
        data_pos_values = [element['data-pos'] for element in japanese_word_elements]
        return data_pos_values

    @staticmethod
    def jisho_parse_html_parser(jisho_html: str) -> list:

    # This function is intended to recieve the html zenbar section for a single sentence. But will handle multiple sentences.
    # Can be postprocessed to break at the . period separator in japanese

        soup = BeautifulSoup(jisho_html, 'html.parser')

        list_of_li_elements = soup.find_all('li', class_='japanese_word')

        regex_for_pos_tag = r'data-pos="([A-Za-z\s]+)"'
        regex_for_japanese_word = r'data-word="([A-Za-z0-9\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\u3000-\u303F\uFF65-\uFF9F]+)"'
        regex_for_Punctuation_symbols = r'([\u2000-\u206F\u3000-\u303F\uFF01-\uFF0F\uFF1A-\uFF20\uFF3B-\uFF40\uFF5B-\uFF65]+)'

        pos_tag_pattern = re.compile(regex_for_pos_tag, re.IGNORECASE)
        puctuation_pattern = re.compile(regex_for_Punctuation_symbols, re.IGNORECASE)
        data_word_pattern = re.compile(regex_for_japanese_word, re.IGNORECASE)

        list_of_pos_tags = list()
        list_of_words = list()

        for li_element in list_of_li_elements:
        # In this loop it is important to ensure that an elements are being added simultaneously to both lists, else the zip
        # Function at the end will fail.
            try:
                pos_tag_match = pos_tag_pattern.search(str(li_element))

                if pos_tag_match is None:
                    list_item_text_content = li_element.get_text
                    puctuation_match = puctuation_pattern.search(str(list_item_text_content))

                    if puctuation_match is not None:
                        pos_tag_match = 'Punctuation'
                        list_of_pos_tags.append(pos_tag_match)

                    else:
                        pos_tag_match = 'NONE'
                        list_of_pos_tags.append(pos_tag_match)
                else:
                    pos_tag_match = pos_tag_match.group(1)
                    list_of_pos_tags.append(pos_tag_match)

                # print(pos_tag_match)
            except Exception as e2:
                logger.error(f'{e2}')
                pos_tag_match = 'ERROR'
                list_of_pos_tags.append(pos_tag_match)
                pass

            try:

                word_match = data_word_pattern.search(str(li_element))

                if word_match is None:
                    list_item_text_content = li_element.get_text
                    puctuation_match = puctuation_pattern.search(str(list_item_text_content))

                    if puctuation_match is not None:
                        word_match = puctuation_match.group(1)
                        list_of_words.append(word_match)

                    else:
                        word_match = 'NONE'
                        list_of_words.append(word_match)

                else:
                    word_match = word_match.group(1)
                    list_of_words.append(word_match)

            except Exception as e2:
                logger.error(f'{e2}')
                word_match = 'ERROR'
                list_of_words.append(word_match)
                pass

        list_of_word_pos_tuples = [(word, pos_tag) for word, pos_tag in zip(list_of_words, list_of_pos_tags)]

        # print(list_of_pos_tags)
        # print(len(list_of_pos_tags))
        # print(list_of_words)
        #
        # print(len(list_of_words))
        # print(list_of_word_pos_tuples)
        # print(len(list_of_word_pos_tuples))

        return list_of_word_pos_tuples

    @staticmethod
    def add_type_to_words(japanese_text):
        pos_mapping = {
            '名詞': 'Noun',
            '動詞': 'Verb',
            '形容詞': 'Adjective',
            '副詞': 'Adverb',
            '助詞': 'Particle',
            '助動詞': 'Auxiliary verb',
            '記号': 'Symbol',
            'フィラー': 'Filler',
            '接続詞': 'Conjunction',
            '接頭詞': 'Prefix',
            '感動詞': 'Interjection',
            '未知語': 'Unknown',
            'その他': 'Other'
        }
        # Create an instance of the MeCab Tagger
        tagger = MeCab.Tagger('-r /dictionaries -d /dictionaries/mydic')

        # Parse the Japanese text
        parsed_text = tagger.parse(japanese_text)

        # Split the parsed text into individual lines
        lines = parsed_text.split('\n')

        # Process each line to extract the word and convert it to Romaji
        processed_lines = []
        for line in lines:
            if line == 'EOS':
                break
            else:
                # Split the line by tabs to extract the word and its features
                parts = line.split('\t')

                # Extract the word from the parts
                word = parts[0]

                # Extract the features from the parts
                features = parts[1].split(',')

                # Extract the most common meaning (part-of-speech) from the features
                pos = features[0]

                # Map the Japanese part-of-speech to its English equivalent
                english_pos = pos_mapping.get(pos)

                # Add the English part-of-speech in brackets after the word
                word_with_meaning = f"{word} ({english_pos})"

                # Append the processed line to the list
                processed_lines.append(word_with_meaning)

        # Join the processed lines to form the final text
        final_text = ' '.join(processed_lines)

        return final_text

    @staticmethod
    def tag_pos(text):
        mecab = MeCab.Tagger("-Ochasen")
        node = mecab.parse(text).split('\n')
        result = []

        for i in node[:-2]:
            col = i.split('\t')
            word = col[0]
            pos = col[3].split('-')[0]
            result.append(f'{word}({pos})')

        return ' '.join(result)


    @staticmethod
    def tag_pos_sudachi(text):
        dict_obj = Dictionary(dict_type='full')
        tokenizer_obj = dict_obj.create()

        # Manual mapping from Japanese POS tags to English equivalents
        pos_map = {
            "名詞": "noun",
            "動詞": "verb",
            "形容詞": "adjective",
            "副詞": "adverb",
            "接続詞": "conjunction",
            "助詞": "particle",
            "助動詞": "auxiliary verb",
            "感動詞": "interjection",
            "記号": "symbol",
            "連体詞": "adnominal",
            "代名詞": "pronoun",
            "フィラー": "filler",
            "未知語": "unknown",
            "補助記号": "symbol",
            "形状詞": "na-adjective"
        }

        result = []

        tokens = tokenizer_obj.tokenize(text)
        # print(tokens.get_internal_cost())
        # print(tokens.__repr__())
        # token = tokens[0]
        # print(token.__repr__())
        # print(f'SURFACE: {token.surface()}')
        # print(f'RAW SURFACE: {token.raw_surface()}')
        # print(f'DICTIONARY_FORM: {token.dictionary_form()}')
        # print(f'DICTIONARY ID: {token.dictionary_id()}')
        # print(f'NORMALIZED FORM: {token.normalized_form()}')

        for token in tokenizer_obj.tokenize(text):
            word = token.surface()
            pos_japanese = token.part_of_speech()[0]

            # Map the Japanese POS tag to an English equivalent if possible
            pos_english = pos_map.get(pos_japanese, pos_japanese)
            result.append((word, pos_english))
        print(''.join(f'{word}:{pos_english}' for (word, pos_english) in result))

        return result



# print(TextSplitter.split_para_to_list_of_lines(test_text))

# print(f'SUDACHI: {Parser.tag_pos_sudachi(test_tokeizer)}')
# print(f'MeCAB: {Parser.add_type_to_words(test_tokeizer)}')