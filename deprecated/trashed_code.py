NEVER RUN

def get_list_of_lis(html_content):

    soup = BeautifulSoup(html_content, 'html.parser') #the second argument defines the parser to be used. In this case the html parser that is bundled with python

    li_tags = soup.find_all('li')
    print(li_tags)
    print(len(li_tags))


    li_text_list = [li.get_text() for li in li_tags]
    print(li_text_list)

    pos_list = list()


    japanese_word_elements = soup.find_all('li', class_='japanese_word')
    # print(japanese_word_elements)
    # print(type(str(japanese_word_elements)))
    # print(len(japanese_word_elements))

    regex_for_pos_tag = r'data-pos="([A-Za-z]+)"'
    # Extract and return the values of data-pos

    pattern = re.compile(regex_for_pos_tag, re.IGNORECASE)
    matches = pattern.finditer(str(japanese_word_elements))

    print([match.group(1) for match in matches])


class ConfiguredHTMLParser(HTMLParser):
    DATA = []
    STARTTAG = []

    def handle_data(self, data: str) -> None:
        self.DATA.append(data)

    def h


# def jisho_parse_html_parser(jisho_parse_html: str) -> list:

parser = ConfiguredHTMLParser()
parser.feed(jisho_test_html)

extracted_list = parser.DATA
trimmed_list = [item for item in extracted_list if not FundamentalPatterns.contains_only_whitespace(item)]

print(trimmed_list)

    @property
    def name(self):
        return self.name

    @name.setter
    def name(self, name: str):
        self.name = name


class RZParagraph(RZChapter):
    def __init__(self,
                 arc_number: int,
                 chapter_number: int,
                 chapter_raw_name: str,
                 paragraph_index: int,
                 paragraph_raw_text: str
                 ):
        # this method calls a method from the parent class from within a child class method
        super().__init__(
            arc_number, chapter_number, chapter_raw_name
        )
        # validation
        assert paragraph_index >= 0, f'Paragraph index cannot be a negative integer'

        # assignment
        self.index = paragraph_index
        self.uid = f'{arc_number}_{chapter_number}_{paragraph_index}'
        self.raw_text = paragraph_raw_text

    def __repr__(self):
        return self.uid