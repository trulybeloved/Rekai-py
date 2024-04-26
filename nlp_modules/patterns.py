import string


class Regex:

    japanese_and_english = r'\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\u3000-\u303F\uFF65-\uFF9F\u0020-\u007E\uFF01-\uFF5E\u2000-\u206F\uFF01-\uFF0F\uFF1A-\uFF20\uFF3B-\uFF40\uFF5B-\uFF65'

    # matches any text that is bounded by
    anything_single_quoted = r'「(.)*」' # will select match anything that is single quoted anywhere within the text
    anything_double_quoted = r'『(.)*』'

    double_quoted_within_single_quoted = r'^「(.)*(『.*』)+(.)*」$'
    # bounded by patterns. Will only match if entire string is bounded, i.e. starts and ends with said characters.
    anything_bounded_by_single_quotes = r'^「(.)*」$'
    anything_bounded_by_double_quotes = r'^『(.)*』$'

    anything_bounded_by_multiple_single_quotes = r'^「{2,}(.)*」{2,}$'
    anything_bounded_by_multiple_double_quotes = r'^『{2,}(.)*』{2,}$'

    single_quoted_japanese_text = r'「([\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\u3000-\u303F\uFF65-\uFF9F\u2000-\u206F\uFF01-\uFF0F\uFF1A-\uFF20\uFF3B-\uFF40\uFF5B-\uFF65]*)」'
    singe_quoted_punctuation_only = r'「([\u2000-\u206F\uFF01-\uFF0F\uFF1A-\uFF20\uFF3B-\uFF40\uFF5B-\uFF65]+)」'

    # characters
    any_katakana = r'[\u30A1-\u30FA\u30FD-\u30FE\u31F0-\u31FF\u32D0-\u32FE\u3300-\u3357\uFF66-\uFF9D]'
    any_hiragana = r'[\u3041-\u3096\u3099-\u309F]'
    any_kanji = r'[\u4E00-\u9FFF\u3400-\u4DBF]'
    any_single_kanji = r'[\u4E00-\u9FFF]'
    continuous_blocks_of_kanji = r'([\u4E00-\u9FFF]+)' # Single or multiple, but continuous
    any_single_kana = r'^([\u3041-\u3096\u3099-\u309F])$'
    same_hiragana_repeated = r'^([\u3041-\u3096\u3099-\u309F])\1+$'

    # jisho_parse_html
    jisho_pos_tag = r'data-pos="([A-Za-z\s]+)"'
    jisho_japanese_word = r'data-word="([A-Za-z0-9\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\u3000-\u303F\uFF65-\uFF9F]+)"'
    jisho_punctuation_symbols = r'([\u2000-\u206F\u3000-\u303F\uFF01-\uFF0F\uFF1A-\uFF20\uFF3B-\uFF40\uFF5B-\uFF65]+)'

    # JNLP.TextSplitter.regex_split
    pattern_for_line = r'([^。！？]*[。！？"」』、]+)'
    pattern_for_clause = r'([^。！？、…―]*[。！？、…"」』―]+)'


class Charsets:

    HIRAGANA = {
        'ー', 'ぁ', 'あ', 'ぃ', 'い', 'ぅ', 'う', 'ぇ', 'え', 'ぉ', 'お', 'か', 'が', 'き', 'ぎ', 'く', 'ぐ',
        'け', 'げ', 'こ', 'ご', 'さ', 'ざ', 'し', 'じ', 'す', 'ず', 'せ', 'ぜ', 'そ', 'ぞ', 'た', 'だ', 'ち',
        'ぢ', 'っ', 'つ', 'づ', 'て', 'で', 'と', 'ど', 'な', 'に', 'ぬ', 'ね', 'の', 'は', 'ば', 'ぱ', 'ひ',
        'び', 'ぴ', 'ふ', 'ぶ', 'ぷ', 'へ', 'べ', 'ぺ', 'ほ', 'ぼ', 'ぽ', 'ま', 'み', 'む', 'め', 'も', 'ゃ',
        'や', 'ゅ', 'ゆ', 'ょ', 'よ', 'ら', 'り', 'る', 'れ', 'ろ', 'ゎ', 'わ', 'ゐ', 'ゑ', 'を', 'ん', '゛',
        '゜'}

    KATAKANA = {
        '゠', 'ァ', 'ア', 'ィ', 'イ', 'ゥ', 'ウ', 'ェ', 'エ', 'ォ', 'オ', 'カ', 'ガ', 'キ', 'ギ', 'ク', 'グ',
        'ケ', 'ゲ', 'コ', 'ゴ', 'サ', 'ザ', 'シ', 'ジ', 'ス', 'ズ', 'セ', 'ゼ', 'ソ', 'ゾ', 'タ', 'ダ', 'チ',
        'ヂ', 'ッ', 'ツ', 'ヅ', 'テ', 'デ', 'ト', 'ド', 'ナ', 'ニ', 'ヌ', 'ネ', 'ノ', 'ハ', 'バ', 'パ', 'ヒ',
        'ビ', 'ピ', 'フ', 'ブ', 'プ', 'ヘ', 'ベ', 'ペ', 'ホ', 'ボ', 'ポ', 'マ', 'ミ', 'ム', 'メ', 'モ', 'ャ',
        'ヤ', 'ュ', 'ユ', 'ョ', 'ヨ', 'ラ', 'リ', 'ル', 'レ', 'ロ', 'ヮ', 'ワ', 'ヰ', 'ヱ', 'ヲ', 'ン', 'ヴ',
        'ヵ', 'ヶ', 'ヷ', 'ヸ', 'ヹ', 'ヺ', '・', 'ー', 'ヽ', 'ヾ'}

    PUNCTUATION = {
        '　', '、', '。', '〃', '〄', '々', '〆', '〇', '〈', '〉', '《', '》', '「', '」', '『', '』', '【',
        '】', '〒', '〓', '〔', '〕', '〖', '〗', '〘', '〙', '〚', '〛', '〜', '〝', '〞', '〟', '〠', '〡',
        '〢', '〣', '〤', '〥', '〦', '〧', '〨', '〩', '〪', '〫', '〬', '〭', '〮', '〯', '〰', '〱', '〲', '〳',
        '〴', '〵', '〶', '〷', '〸', '〹', '〺', '〻', '〼', '〽', '〾', '〿', '！', '＂', '＃', '＄', '％',
        '＆', '＇', '（', '）', '＊', '＋', '，', '－', '．', '／', '：', '；', '＜', '＝', '＞', '？', '［',
        '＼', '］', '＾', '＿', '｀', '｛', '｜', '｝', '～', '｟', '｠', '｡', '｢', '｣', '､', '･', 'ー', '※',
        ' ', ' ', ' ', ' ', "«", "»", ' ', ' ', ' ', ' ', ' ', ' ', ' ',
        '​', '‌', '‍', '‎', '‏', '‐', '‑', '‒', '–', '—', '―', '‖', '‗', '‘', '’', '‚', '‛',
        '“', '”', '„', '‟', '†', '‡', '•', '‣', '․', '‥', '…', '‧', ' ', ' ', '‪', '‫', '‬',
        '‭', '‮', ' ', '‰', '‱', '′', '″', '‴', '‵', '‶', '‷', '‸', '‹', '›', '‼', '‽', '‾', '‿',
        '⁀', '⁁', '⁂', '⁃', '⁄', '⁅', '⁆', '⁇', '⁈', '⁉', '⁊', '⁋', '⁌', '⁍', '⁎', '⁏', '⁐', '⁑', '⁒', '⁓',
        '⁔', '⁕', '⁖', '⁗', '⁘', '⁙', '⁚', '⁛', '⁜', '⁝', '⁞', ' ', '⁠', '⁦', '⁧', '⁨', '⁩',
        '«', '»', '×', "△", "▼"} | set(string.punctuation) | set(string.whitespace)

    EXPRESSIONS = {'ー', 'ぁ', 'あ', 'ぃ', 'い', 'ぅ', 'う', 'ぇ', 'え', 'ぉ', 'お', 'っ', 'つ'} #  kana that are often used to end expressive dialogues
