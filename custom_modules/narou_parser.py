from bs4 import BeautifulSoup

JAPANESE_NUMBERS_UNICODE_MAP = {
    "０": "0", "１": "1", "２": "2", "３": "3", "４": "4", "５": "5", "６": "6", "７": "7", "８": "8", "９": "9"
}

JAPANESE_FULL_WIDTH_ALPHABETS_UNICODE_MAP = {
    "Ａ": "A", "Ｂ": "B", "Ｃ": "C", "Ｄ": "D", "Ｅ": "E", "Ｆ": "F", "Ｇ": "G", "Ｈ": "H", "Ｉ": "I", "Ｊ": "J", "Ｋ": "K",
    "Ｌ": "L", "Ｍ": "M", "Ｎ": "N", "Ｏ": "O", "Ｐ": "P", "Ｑ": "Q", "Ｒ": "R", "Ｓ": "S", "Ｔ": "T", "Ｕ": "U", "Ｖ": "V",
    "Ｗ": "W", "Ｘ": "X", "Ｙ": "Y", "Ｚ": "Z", "ａ": "a", "ｂ": "b", "ｃ": "c", "ｄ": "d", "ｅ": "e", "ｆ": "f", "ｇ": "g",
    "ｈ": "h", "ｉ": "i", "ｊ": "j", "ｋ": "k", "ｌ": "l", "ｍ": "m", "ｎ": "n", "ｏ": "o", "ｐ": "p", "ｑ": "q", "ｒ": "r",
    "ｓ": "s", "ｔ": "t", "ｕ": "u", "ｖ": "v", "ｗ": "w", "ｘ": "x", "ｙ": "y", "ｚ": "z"
}

RZ_JAPANESE_ARC_LABELS_MAP = {
    "第一章": "1",
    "第二章": "2",
    "第三章": "3",
    "第四章": "4",
    "第五章": "5",
    "第六章": "6",
    "第七章": "7",
    "第八章": "8",
    "第九章": "9",
    "第十章": "10",
    "第十一章": "11",
    "第十二章": "12"
}

RZ_JAPANESE_EXTRA_LABEL = "リゼロＥＸ"

RZ_JAPANESE_INTERLUDE_LABEL = "幕間"


def parse_chapter_title(chapter_title: str) -> dict:
    results = {}

    def get_arc_number(_jp_chapter_label: str) -> str:
        for key, value in RZ_JAPANESE_ARC_LABELS_MAP.items():
            if key in _jp_chapter_label:
                return value

    def get_chapter_number(_jp_chapter_label: str) -> str:
        if RZ_JAPANESE_INTERLUDE_LABEL in _jp_chapter_label:
            return 'Interlude'

        for key, value in RZ_JAPANESE_ARC_LABELS_MAP.items():
            _jp_chapter_label = _jp_chapter_label.replace(key, '')

        for key, value in JAPANESE_NUMBERS_UNICODE_MAP.items():
            _jp_chapter_label = _jp_chapter_label.replace(key, value)

        for key, value in JAPANESE_FULL_WIDTH_ALPHABETS_UNICODE_MAP.items():
            _jp_chapter_label = _jp_chapter_label.replace(key, value)

        chapter_number = _jp_chapter_label

        return chapter_number

    title_components = chapter_title.split('　')
    jp_chapter_label = title_components[0]
    jp_chapter_name = title_components[1]

    if jp_chapter_label == RZ_JAPANESE_EXTRA_LABEL:
        results['chapter_type'] = 'EX'
        results['arc_number'] = None
        results['chapter_number'] = None
        results['jp_chapter_name'] = jp_chapter_name
        return results

    else:
        arc_number = get_arc_number(jp_chapter_label)
        chapter_number = get_chapter_number(jp_chapter_label)

        results['chapter_type'] = 'MAIN'
        results['arc_number'] = arc_number
        results['chapter_number'] = chapter_number
        results['jp_chapter_name'] = jp_chapter_name
        return results


def generate_chapter_id(chapter_parse_results) -> str:
    if chapter_parse_results['chapter_type'] == 'EX':
        chapter_name = chapter_parse_results['jp_chapter_name']
        return f'rzex{chapter_name}'

    if chapter_parse_results['chapter_type'] == 'MAIN':
        arc_number = chapter_parse_results['arc_number']
        chapter_number = chapter_parse_results['chapter_number']
        return f'rza{arc_number}c{chapter_number}'


def parse_chapter_html(chapter_html: str) -> str:
    chapter_soup = BeautifulSoup(chapter_html, 'html.parser')
    paragraphs = chapter_soup.find_all('p')

    # Needs an implementation to detect ruby tags
    trimmed_paragraphs = [f'{paragraph.text}' for paragraph in paragraphs if paragraph.text]
    print(trimmed_paragraphs)
    chapter_text = ''
    for paragraph in trimmed_paragraphs:
        chapter_text += f'{paragraph}\n\n'

    return chapter_text


def parse_narou_chapter_html(scraper_results: dict) -> dict:
    parse_results = {}
    parse_results['narou_link'] = scraper_results['scraped_url']
    parse_results['chapter_uid'] = str(scraper_results['scraped_url']).replace(
        'https://ncode.syosetu.com/n2267be/', '').replace('/', '')
    chapter_title = BeautifulSoup(scraper_results['scrape_results']['.novel_subtitle'], 'html.parser').text
    parse_results['chapter_title'] = chapter_title
    chapter_title_parse_results = parse_chapter_title(chapter_title)
    parse_results['chapter_id'] = generate_chapter_id(chapter_title_parse_results)
    parse_results.update(chapter_title_parse_results)

    chapter_text = str()
    chapter_text += f'{chapter_title}\n\n'
    chapter_text += parse_chapter_html(scraper_results['scrape_results']['#novel_honbun'])
    parse_results['chapter_text'] = chapter_text

    return parse_results


def parse_narou_index_html(index_html) -> list:
    index_soup = BeautifulSoup(index_html, 'html.parser')
    index_entires = index_soup.find_all('a')
    chapter_links = []

    for a_tag in index_entires:
        href = a_tag.get('href')
        chapter_link = f'https://ncode.syosetu.com{href}'
        chapter_links.append(chapter_link)

    return chapter_links

