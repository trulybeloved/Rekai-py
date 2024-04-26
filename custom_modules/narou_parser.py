from bs4 import BeautifulSoup


def parse_chapter_html(chapter_html: str) -> str:
    chapter_soup = BeautifulSoup(chapter_html, 'html.parser')
    paragraphs = chapter_soup.find_all('p')
    print(paragraphs)
    for paragraph in paragraphs:
        if '<ruby>' in str(paragraph):
            print(paragraph)
            print(paragraph.text)

    trimmed_paragraphs = [f'{paragraph.text}' for paragraph in paragraphs if paragraph.text]
    print(trimmed_paragraphs)
    jp_text = ''
    for paragraph in trimmed_paragraphs:
        jp_text += f'{paragraph}\n\n'

    print(jp_text)



with open('chapter_html.html', 'r', encoding='utf-8') as html_file:
    html = html_file.read()

parse_chapter_html(html)