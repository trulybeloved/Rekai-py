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

    class DatabaseHelper:

        def __init__(self, database_name: str, datastores_path: str) -> None:
            """ Initializes the database manager class and opens a connection to the specified database"""
            self.database_name = database_name
            self.datastores_path = datastores_path
            self.connection = sqlite3.connect(self.datastores_path)

        def insert_into_table_dynamic(self, table_name: str, columns: list, values: list):
            cursor = self.connection.cursor()

            processed_values = []
            for value in values:
                if isinstance(value, int):
                    # for INTEGER
                    processed_values.append(value)
                elif isinstance(value, str):
                    if value.endswith(('.txt', '.pdf', '.png', '.jpg', '.jpeg', '.gif')):
                        # for BLOB
                        blob_data = self.convert_file_to_blob(value)
                        processed_values.append(sqlite3.Binary(blob_data))
                    else:
                        # for TEXT
                        processed_values.append(value)
                else:
                    raise ValueError(f'Unsupported data type: {type(value)}')

            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['?' for _ in values])})"
            cursor.execute(query, tuple(processed_values))
            self.connection.commit()

        @staticmethod
        def convert_file_to_blob(file):
            with open(file, 'rb') as f:
                blob = f.read()
            return blob

    class DatabaseManager:

        def __init__(self, database_name: str, datastores_path: str) -> None:
            """ Initializes the database manager class and opens a connection to the specified database"""
            self.database_name = database_name
            self.datastores_path = datastores_path
            self.connection = sqlite3.connect(self.datastores_path)

        def close_connection(self) -> None:
            self.connection.close()

        def create_table(self, table_name: str, columns: list) -> None:
            cursor = self.connection.cursor()
            query = f"CREATE TABLE {table_name} ({', '.join(columns)})"
            cursor.execute(query)
            self.connection.commit()

        def insert_into_table(self, table_name: str, columns: list, values: list) -> None:
            cursor = self.connection.cursor()
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['?' for _ in values])})"
            cursor.execute(query, values)
            self.connection.commit()

        def update_table(self, table_name: str, set_columns: list, set_values: list, where_column: str, where_value: str):
            cursor = self.connection.cursor()
            query = f"UPDATE {table_name} SET {', '.join([f'{col} = ?' for col in set_columns])} WHERE {where_column} = ?"
            values = [*set_values, where_value]
            cursor.execute(query, values)
            self.connection.commit()

        def select_from_table(self, table_name, select_columns, where_column=None, where_value=None):
            cursor = self.connection.cursor()
            query = f"SELECT {', '.join(select_columns)} FROM {table_name}"
            if where_column and where_value:
                query += f" WHERE {where_column} = ?"
                cursor.execute(query, (where_value,))
            else:
                cursor.execute(query)
            return cursor.fetchall()

        def delete_from_table(self, table_name, where_column, where_value):
            cursor = self.connection.cursor()
            query = f"DELETE FROM {table_name} WHERE {where_column} = ?"
            cursor.execute(query, (where_value,))
            self.connection.commit()


        def insert_integer_into_table(self, table_name, column_name, value):
            cursor = self.connection.cursor()
            query = f"INSERT INTO {table_name} ({column_name}) VALUES (?)"
            cursor.execute(query, (value,))
            self.connection.commit()

        def insert_blob_into_table(self, table_name, column_name, file):
            cursor = self.connection.cursor()
            blob_data = self.convert_file_to_blob(file)
            query = f"INSERT INTO {table_name} ({column_name}) VALUES (?)"
            cursor.execute(query, (sqlite3.Binary(blob_data),))
            self.connection.commit()

        @staticmethod
        def convert_file_to_blob(file):
            with open(file, 'rb') as f:
                blob = f.read()
            return blob
    # db = DatabaseManager("my_db",r"C:\Users\prav9\OneDrive\Desktop\Coding\MTL\Rekai\my_db.db")
    # # db.create_table("users", ["id INTEGER PRIMARY KEY", "name TEXT", "email TEXT"])
    # db.insert_into_table("users", ["name", "email"], ["John Doe", "john.doe@example.com"])
    # print(db.select_from_table("users", ["name", "email"]))
    # db.update_table("users", ["email"], ["johndoe@example.com"], "name", "John Doe")
    # print(db.select_from_table("users", ["name", "email"]))
    # # db.delete_from_table("users", "name", "John Doe")
    # # print(db.select_from_table("users", ["name", "email"]))
    # db.close_connection()

    class DatabaseIO(ABC):


        @abstractmethod
        def query(self):
            pass

        @abstractmethod
        def insert(self) -> None:
            pass

        @abstractmethod
        def delete(self):
            pass

dict = {
    1:{
        "para_raw":"para_raw_text",
        "preprocessed":"preprocessed_text",
        "raw_lines":{
            1:{
                "line_raw":"line_raw_text",
                "clauses":{
                    1:{
                        "clause_raw":"clause_raw_text"
                    }
                }
            }
        }
    }
}

dict2 = {
    1:{
        "para_raw":"para_raw_text",
        "preprocessed":"preprocessed_text",
        "raw_lines": [("line1",["clause1", "clause2"])]
    }
}
list_structure = \
    [
        (
            int(paranumber),
            "para_raw",
            [
                (
                    int(linenumber),
                    "line_raw",
                    [
                        (
                            int(clausenumebr),
                            "clause_raw"
                        )
                    ]
                )
            ]
        )
    ]

# @dataclass
class ReZeroChapter:
    """
    # arc_number: int
    # chapter_number: int
    # chapter_raw_name: str
    # chapter_raw_text: str
    # chapter_type: str = 'Typical' | 'Special'
    # content_type: str = 'WebNovel' | 'LightNovel' | 'SideContent'

    # number_of_paragraphs: int = None
    # list_of_para_index_raw_tuples: list = None
    # list_of_para_index_line_raw_tuples: list = None
    # list_of_arc_chapter_para_index_line_raw_tuples: list = None

    """

    def __init__(self,
                 arc_number: int,
                 chapter_number: int,
                 chapter_raw_name: str,
                 chapter_raw_text: str,
                 chapter_type: str = 'Typical',
                 content_type: str = 'WebNovel'
                 ):

        # validation
        assert arc_number >= 0, f'Arc number cannot be a negative integer'
        assert chapter_number >= 0, f'Chapter number cannot be a negative integer'
        assert isinstance(chapter_raw_name, str), f'Chapter Raw Name is not a string.'
        assert isinstance(chapter_raw_text, str), f'Chapter Raw text is not a string.'
        assert len(chapter_raw_text) > 0, f'Chapter Raw text is empty.'
        assert isinstance(chapter_type, str), f'Chapter Raw text is not a string.'
        assert isinstance(content_type, str), f'Chapter Raw text is not a string.'

        # assignment and generation of core instance attributes
        self.arc_number = arc_number
        self.chapter_number = chapter_number
        self.raw_name = chapter_raw_name
        self.raw_text = chapter_raw_text
        self.chapter_type = chapter_type
        self.content_type = content_type

        logger.info(f'A new instance of {self.__class__.__name__} was initialized')

    def display_info(self):
        """Display information about the chapter."""
        print(f'{self.__class__.__name__}', )

        for attr, value in vars(self).items():
            print(f"{attr}: {value}", end='\n')

    def __repr__(self):
        """Return a string representation of the object."""
        attributes = '| '.join(f'{key} = {value}\n' for key, value in vars(self).items())
        return f'{self.__class__.__name__}({attributes})'

    def set_url(self, url):
        """Set the URL for the chapter."""
        self.url = url

    def extract_paragraphs(self):
        """Extract, Process and Count the number of paragraphs in the raw text."""

        if self.raw_text:
            paragraphs = BasicNLP.TextSplitter.splitlines_to_list(
                self.raw_text,
                keepends=False,
                strip_each_line=True,
                # This is the default. It will remove the \u3000 whitespace from start of paragraphs
                trim_list=True
            )
            self.number_of_paragraphs = len(paragraphs)
            self.list_of_paragraphs = paragraphs
            self.list_of_para_paratext_tuples = [(index + 1, paratext) for index, paratext in enumerate(paragraphs)]
            self.list_of_para_line_linetext_tuples = []
            for (para, paratext) in self.list_of_para_paratext_tuples:
                lines = JNLP.TextSplitter.split_para_to_list_of_lines(
                    paratext,
                    strip_each_line=False,
                    trim_list=True  # IF FALSE AN EMPTY STRING IS ADDED TO THE END OF THE LIST BY THE SPLIT FUNCTION
                )
                for line_index, line in enumerate(lines):
                    para_line_linetext_tuple = (para, line_index + 1, line)
                    self.list_of_para_line_linetext_tuples.append(para_line_linetext_tuple)

        else:
            logger.error('Paragraphs could not be extracted as raw_text is empty')


#
# chapter = ReZeroChapter(raw_text_chapter_arc, raw_text_chapter_number, raw_text_chapter_name,
#                         raw_text_chapter_content)
#
# chapter.extract_paragraphs()
#
# list_of_paragraphs = chapter.list_of_paragraphs
# list_of_index_para_tuples = chapter.list_of_para_paratext_tuples
# list_of_index_para_line_tuples = chapter.list_of_para_line_linetext_tuples


# rzchap = RZChapter(1, 1, "Chapter 1")
# chapter.display_info()

mylist = [(1, Lines(source_paragraph='――これは本気でマズイことになった。', list_of_lines=['――これは本気でマズイことになった。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='――これは本気でマズイことになった。', list_of_clauses=['――これは本気でマズイことになった。'], number_of_clauses=1))])), (2, Lines(source_paragraph='一文無しで途方に暮れながら、彼の心中はそんな一言で埋め尽くされていた。', list_of_lines=['一文無しで途方に暮れながら、彼の心中はそんな一言で埋め尽くされていた。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='一文無しで途方に暮れながら、彼の心中はそんな一言で埋め尽くされていた。', list_of_clauses=['一文無しで途方に暮れながら、', '彼の心中はそんな一言で埋め尽くされていた。'], number_of_clauses=2))])), (3, Lines(source_paragraph='一文無しというのは正確ではない。財布はポケットの中に入っているし、やや小銭が多くてお札が少ない点を除けば全財力には違いない。', list_of_lines=['一文無しというのは正確ではない。', '財布はポケットの中に入っているし、やや小銭が多くてお札が少ない点を除けば全財力には違いない。'], number_of_lines=2, list_of_clause_object_tuples=[(1, Clauses(source_line='一文無しというのは正確ではない。', list_of_clauses=['一文無しというのは正確ではない。'], number_of_clauses=1)), (2, Clauses(source_line='財布はポケットの中に入っているし、やや小銭が多くてお札が少ない点を除けば全財力には違いない。', list_of_clauses=['財布はポケットの中に入っているし、', 'やや小銭が多くてお札が少ない点を除けば全財力には違いない。'], number_of_clauses=2))])), (4, Lines(source_paragraph='地元から一番近いショッピングモールまで出て、本屋で買い物して昼飯を食べてくるぐらいの余裕は持てる懐具合。にも関わらず、一文無しと表現するしかない。', list_of_lines=['地元から一番近いショッピングモールまで出て、本屋で買い物して昼飯を食べてくるぐらいの余裕は持てる懐具合。', 'にも関わらず、一文無しと表現するしかない。'], number_of_lines=2, list_of_clause_object_tuples=[(1, Clauses(source_line='地元から一番近いショッピングモールまで出て、本屋で買い物して昼飯を食べてくるぐらいの余裕は持てる懐具合。', list_of_clauses=['地元から一番近いショッピングモールまで出て、', '本屋で買い物して昼飯を食べてくるぐらいの余裕は持てる懐具合。'], number_of_clauses=2)), (2, Clauses(source_line='にも関わらず、一文無しと表現するしかない。', list_of_clauses=['にも関わらず、', '一文無しと表現するしかない。'], number_of_clauses=2))])), (5, Lines(source_paragraph='なにせ、', list_of_lines=['なにせ、'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='なにせ、', list_of_clauses=['なにせ'], number_of_clauses=1))])), (6, Lines(source_paragraph='「やっぱ、貨幣価値とかって全然違うんだよな……」', list_of_lines=['「やっぱ、貨幣価値とかって全然違うんだよな……」'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='「やっぱ、貨幣価値とかって全然違うんだよな……」', list_of_clauses=['「やっぱ、', '貨幣価値とかって全然違うんだよな……」'], number_of_clauses=2))])), (7, Lines(source_paragraph='手の中の十円玉――希少な『ギザ十』を指で弾いて、少年は長いため息をこぼした。', list_of_lines=['手の中の十円玉――希少な『ギザ十』を指で弾いて、少年は長いため息をこぼした。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='手の中の十円玉――希少な『ギザ十』を指で弾いて、少年は長いため息をこぼした。', list_of_clauses=['手の中の十円玉――希少な『ギザ十』を指で弾いて、', '少年は長いため息をこぼした。'], number_of_clauses=2))])), (8, Lines(source_paragraph='これといった特徴のない少年だ。短い黒髪に、高くも低くもない平均的な身長。体格は鍛えているのかやや筋肉質で、安物のグレーのジャージと相まってスポーツマン風ではある。', list_of_lines=['これといった特徴のない少年だ。', '短い黒髪に、高くも低くもない平均的な身長。', '体格は鍛えているのかやや筋肉質で、安物のグレーのジャージと相まってスポーツマン風ではある。'], number_of_lines=3, list_of_clause_object_tuples=[(1, Clauses(source_line='これといった特徴のない少年だ。', list_of_clauses=['これといった特徴のない少年だ。'], number_of_clauses=1)), (2, Clauses(source_line='短い黒髪に、高くも低くもない平均的な身長。', list_of_clauses=['短い黒髪に、', '高くも低くもない平均的な身長。'], number_of_clauses=2)), (3, Clauses(source_line='体格は鍛えているのかやや筋肉質で、安物のグレーのジャージと相まってスポーツマン風ではある。', list_of_clauses=['体格は鍛えているのかやや筋肉質で、', '安物のグレーのジャージと相まってスポーツマン風ではある。'], number_of_clauses=2))])), (9, Lines(source_paragraph='三白眼の鋭い目だけが印象的だが、今はその目尻も力なく落ちていて覇気がない。', list_of_lines=['三白眼の鋭い目だけが印象的だが、今はその目尻も力なく落ちていて覇気がない。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='三白眼の鋭い目だけが印象的だが、今はその目尻も力なく落ちていて覇気がない。', list_of_clauses=['三白眼の鋭い目だけが印象的だが、', '今はその目尻も力なく落ちていて覇気がない。'], number_of_clauses=2))])), (10, Lines(source_paragraph='群衆に紛れれば一瞬で見失いそうなほど凡庸な見た目だ。', list_of_lines=['群衆に紛れれば一瞬で見失いそうなほど凡庸な見た目だ。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='群衆に紛れれば一瞬で見失いそうなほど凡庸な見た目だ。', list_of_clauses=['群衆に紛れれば一瞬で見失いそうなほど凡庸な見た目だ。'], number_of_clauses=1))])), (11, Lines(source_paragraph='が、そんな彼を見る人々の視線には『珍奇』なものでも見るような不可解な色が濃い。', list_of_lines=['が、そんな彼を見る人々の視線には『珍奇』なものでも見るような不可解な色が濃い。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='が、そんな彼を見る人々の視線には『珍奇』なものでも見るような不可解な色が濃い。', list_of_clauses=['が、', 'そんな彼を見る人々の視線には『珍奇』なものでも見るような不可解な色が濃い。'], number_of_clauses=2))])), (12, Lines(source_paragraph='当然といえば当然の話――なにせ少年を眺める彼らの中には、ひとりとして『黒髪』のものも『ジャージ姿』のものもいない。', list_of_lines=['当然といえば当然の話――なにせ少年を眺める彼らの中には、ひとりとして『黒髪』のものも『ジャージ姿』のものもいない。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='当然といえば当然の話――なにせ少年を眺める彼らの中には、ひとりとして『黒髪』のものも『ジャージ姿』のものもいない。', list_of_clauses=['当然といえば当然の話――なにせ少年を眺める彼らの中には、', 'ひとりとして『黒髪』のものも『ジャージ姿』のものもいない。'], number_of_clauses=2))])), (13, Lines(source_paragraph='彼らの頭髪は金髪や白髪、茶髪を始めとして緑髪から青髪まで様々で、さらに格好は鎧やら踊子風の衣装やら黒一色のローブやら『それ』らしすぎる。', list_of_lines=['彼らの頭髪は金髪や白髪、茶髪を始めとして緑髪から青髪まで様々で、さらに格好は鎧やら踊子風の衣装やら黒一色のローブやら『それ』らしすぎる。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='彼らの頭髪は金髪や白髪、茶髪を始めとして緑髪から青髪まで様々で、さらに格好は鎧やら踊子風の衣装やら黒一色のローブやら『それ』らしすぎる。', list_of_clauses=['彼らの頭髪は金髪や白髪、', '茶髪を始めとして緑髪から青髪まで様々で、', 'さらに格好は鎧やら踊子風の衣装やら黒一色のローブやら『それ』らしすぎる。'], number_of_clauses=3))])), (14, Lines(source_paragraph='無遠慮な視線の波にさらされて、少年は腕を組みながら納得するしかない。', list_of_lines=['無遠慮な視線の波にさらされて、少年は腕を組みながら納得するしかない。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='無遠慮な視線の波にさらされて、少年は腕を組みながら納得するしかない。', list_of_clauses=['無遠慮な視線の波にさらされて、', '少年は腕を組みながら納得するしかない。'], number_of_clauses=2))])), (15, Lines(source_paragraph='「つまり、これはあれだな」', list_of_lines=['「つまり、これはあれだな」'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='「つまり、これはあれだな」', list_of_clauses=['「つまり、', 'これはあれだな」'], number_of_clauses=2))])), (16, Lines(source_paragraph='指を鳴らし、自分の方を見る人々に鳴らした指を向けながら、', list_of_lines=['指を鳴らし、自分の方を見る人々に鳴らした指を向けながら、'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='指を鳴らし、自分の方を見る人々に鳴らした指を向けながら、', list_of_clauses=['指を鳴らし、', '自分の方を見る人々に鳴らした指を向けながら'], number_of_clauses=2))])), (17, Lines(source_paragraph='「――異世界召喚もの、ということらしい」', list_of_lines=['「――異世界召喚もの、ということらしい」'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='「――異世界召喚もの、ということらしい」', list_of_clauses=['「――異世界召喚もの、', 'ということらしい」'], number_of_clauses=2))])), (18, Lines(source_paragraph='目の前を、巨大なトカゲ風の生き物に引かれた馬車的な乗り物が横切っていった。', list_of_lines=['目の前を、巨大なトカゲ風の生き物に引かれた馬車的な乗り物が横切っていった。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='目の前を、巨大なトカゲ風の生き物に引かれた馬車的な乗り物が横切っていった。', list_of_clauses=['目の前を、', '巨大なトカゲ風の生き物に引かれた馬車的な乗り物が横切っていった。'], number_of_clauses=2))])), (19, Lines(source_paragraph='※※\u3000※\u3000※\u3000※\u3000※\u3000※\u3000※\u3000※\u3000※\u3000※\u3000※\u3000※', list_of_lines=['※※\u3000※\u3000※\u3000※\u3000※\u3000※\u3000※\u3000※\u3000※\u3000※\u3000※\u3000※'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='※※\u3000※\u3000※\u3000※\u3000※\u3000※\u3000※\u3000※\u3000※\u3000※\u3000※\u3000※', list_of_clauses=['※※\u3000※\u3000※\u3000※\u3000※\u3000※\u3000※\u3000※\u3000※\u3000※\u3000※\u3000※'], number_of_clauses=1))])), (20, Lines(source_paragraph='菜月なつき昴すばるは平成日本生まれのゆとり教育世代出身である。', list_of_lines=['菜月なつき昴すばるは平成日本生まれのゆとり教育世代出身である。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='菜月なつき昴すばるは平成日本生まれのゆとり教育世代出身である。', list_of_clauses=['菜月なつき昴すばるは平成日本生まれのゆとり教育世代出身である。'], number_of_clauses=1))])), (21, Lines(source_paragraph='彼の人生は十七年、その全てを語り尽くすにはそれこそ十七年の時間を必要とする。', list_of_lines=['彼の人生は十七年、その全てを語り尽くすにはそれこそ十七年の時間を必要とする。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='彼の人生は十七年、その全てを語り尽くすにはそれこそ十七年の時間を必要とする。', list_of_clauses=['彼の人生は十七年、', 'その全てを語り尽くすにはそれこそ十七年の時間を必要とする。'], number_of_clauses=2))])), (22, Lines(source_paragraph='それらを割愛し、彼の現在の立場を簡単に説明するのならば『高校三年生にしてひきこもり』となる。', list_of_lines=['それらを割愛し、彼の現在の立場を簡単に説明するのならば『高校三年生にしてひきこもり』となる。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='それらを割愛し、彼の現在の立場を簡単に説明するのならば『高校三年生にしてひきこもり』となる。', list_of_clauses=['それらを割愛し、', '彼の現在の立場を簡単に説明するのならば『高校三年生にしてひきこもり』となる。'], number_of_clauses=2))])), (23, Lines(source_paragraph='詳細に説明するなら、『受験を間近に控えた時期なのに、親の期待もなにもかもうっちゃって自分の殻に閉じこもったどうしようもないクズ』といったところだ。', list_of_lines=['詳細に説明するなら、『受験を間近に控えた時期なのに、親の期待もなにもかもうっちゃって自分の殻に閉じこもったどうしようもないクズ』といったところだ。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='詳細に説明するなら、『受験を間近に控えた時期なのに、親の期待もなにもかもうっちゃって自分の殻に閉じこもったどうしようもないクズ』といったところだ。', list_of_clauses=['詳細に説明するなら、', '『受験を間近に控えた時期なのに、', '親の期待もなにもかもうっちゃって自分の殻に閉じこもったどうしようもないクズ』といったところだ。'], number_of_clauses=3))])), (24, Lines(source_paragraph='ひきこもった理由は特にない。', list_of_lines=['ひきこもった理由は特にない。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='ひきこもった理由は特にない。', list_of_clauses=['ひきこもった理由は特にない。'], number_of_clauses=1))])), (25, Lines(source_paragraph='普通の平日、たまたま「今日は起きるのが面倒だ」となんとなく思い、サボりを実行に移したことが切っ掛けではあった。', list_of_lines=['普通の平日、たまたま「今日は起きるのが面倒だ」となんとなく思い、サボりを実行に移したことが切っ掛けではあった。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='普通の平日、たまたま「今日は起きるのが面倒だ」となんとなく思い、サボりを実行に移したことが切っ掛けではあった。', list_of_clauses=['普通の平日、', 'たまたま「今日は起きるのが面倒だ」となんとなく思い、', 'サボりを実行に移したことが切っ掛けではあった。'], number_of_clauses=3))])), (26, Lines(source_paragraph='そのままずるずると自主休校が増え、気付けば立派に親を泣かせるひきこもり。', list_of_lines=['そのままずるずると自主休校が増え、気付けば立派に親を泣かせるひきこもり。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='そのままずるずると自主休校が増え、気付けば立派に親を泣かせるひきこもり。', list_of_clauses=['そのままずるずると自主休校が増え、', '気付けば立派に親を泣かせるひきこもり。'], number_of_clauses=2))])), (27, Lines(source_paragraph='日がな一日怠惰をむさぼり、コミュニケーション皆無のネットに沈み続け――、', list_of_lines=['日がな一日怠惰をむさぼり、コミュニケーション皆無のネットに沈み続け――、'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='日がな一日怠惰をむさぼり、コミュニケーション皆無のネットに沈み続け――、', list_of_clauses=['日がな一日怠惰をむさぼり、', 'コミュニケーション皆無のネットに沈み続け――'], number_of_clauses=2))])), (28, Lines(source_paragraph='「その結果が異世界召喚か……もはや自分で言ってて意味わかんねぇな」', list_of_lines=['「その結果が異世界召喚か……もはや自分で言ってて意味わかんねぇな」'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='「その結果が異世界召喚か……もはや自分で言ってて意味わかんねぇな」', list_of_clauses=['「その結果が異世界召喚か……もはや自分で言ってて意味わかんねぇな」'], number_of_clauses=1))])), (29, Lines(source_paragraph='改めて状況を再確認して、スバルはもう何度目になるかわからないため息をついた。', list_of_lines=['改めて状況を再確認して、スバルはもう何度目になるかわからないため息をついた。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='改めて状況を再確認して、スバルはもう何度目になるかわからないため息をついた。', list_of_clauses=['改めて状況を再確認して、', 'スバルはもう何度目になるかわからないため息をついた。'], number_of_clauses=2))])), (30, Lines(source_paragraph='先ほどまで好奇の視線を浴びていた通りから場所を移し、今は少し薄暗い路地裏に腰を下ろしている。', list_of_lines=['先ほどまで好奇の視線を浴びていた通りから場所を移し、今は少し薄暗い路地裏に腰を下ろしている。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='先ほどまで好奇の視線を浴びていた通りから場所を移し、今は少し薄暗い路地裏に腰を下ろしている。', list_of_clauses=['先ほどまで好奇の視線を浴びていた通りから場所を移し、', '今は少し薄暗い路地裏に腰を下ろしている。'], number_of_clauses=2))])), (31, Lines(source_paragraph='地面は舗装されていて、現代日本と比較すれば雑な仕事だが悪くはない。', list_of_lines=['地面は舗装されていて、現代日本と比較すれば雑な仕事だが悪くはない。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='地面は舗装されていて、現代日本と比較すれば雑な仕事だが悪くはない。', list_of_clauses=['地面は舗装されていて、', '現代日本と比較すれば雑な仕事だが悪くはない。'], number_of_clauses=2))])), (32, Lines(source_paragraph='「現状が異世界ファンタジーと仮定して、文明はお決まりの中世風ってとこか？\u3000見たとこ機械類はなしで、建材も石材か木材でほぼ統一……」', list_of_lines=['「現状が異世界ファンタジーと仮定して、文明はお決まりの中世風ってとこか？\u3000見たとこ機械類はなしで、建材も石材か木材でほぼ統一……」'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='「現状が異世界ファンタジーと仮定して、文明はお決まりの中世風ってとこか？\u3000見たとこ機械類はなしで、建材も石材か木材でほぼ統一……」', list_of_clauses=['「現状が異世界ファンタジーと仮定して、', '文明はお決まりの中世風ってとこか？\u3000見たとこ機械類はなしで、', '建材も石材か木材でほぼ統一……」'], number_of_clauses=3))])), (33, Lines(source_paragraph='路地裏に腰を下ろすまでに見た光景を思い返し、脳内の情報を整理していく。', list_of_lines=['路地裏に腰を下ろすまでに見た光景を思い返し、脳内の情報を整理していく。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='路地裏に腰を下ろすまでに見た光景を思い返し、脳内の情報を整理していく。', list_of_clauses=['路地裏に腰を下ろすまでに見た光景を思い返し、', '脳内の情報を整理していく。'], number_of_clauses=2))])), (34, Lines(source_paragraph='日頃から妄想にふける時間はたっぷりあったおかげで、『異世界召喚』された際の心構えは上々だ。', list_of_lines=['日頃から妄想にふける時間はたっぷりあったおかげで、『異世界召喚』された際の心構えは上々だ。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='日頃から妄想にふける時間はたっぷりあったおかげで、『異世界召喚』された際の心構えは上々だ。', list_of_clauses=['日頃から妄想にふける時間はたっぷりあったおかげで、', '『異世界召喚』された際の心構えは上々だ。'], number_of_clauses=2))])), (35, Lines(source_paragraph='まずは冷静にその時代の文明、現代日本との衣食住の差異。物理現象の違いや、生息している『人型生物』とのコンタクトが可能かどうか見極める必要がある。', list_of_lines=['まずは冷静にその時代の文明、現代日本との衣食住の差異。', '物理現象の違いや、生息している『人型生物』とのコンタクトが可能かどうか見極める必要がある。'], number_of_lines=2, list_of_clause_object_tuples=[(1, Clauses(source_line='まずは冷静にその時代の文明、現代日本との衣食住の差異。', list_of_clauses=['まずは冷静にその時代の文明、', '現代日本との衣食住の差異。'], number_of_clauses=2)), (2, Clauses(source_line='物理現象の違いや、生息している『人型生物』とのコンタクトが可能かどうか見極める必要がある。', list_of_clauses=['物理現象の違いや、', '生息している『人型生物』とのコンタクトが可能かどうか見極める必要がある。'], number_of_clauses=2))])), (36, Lines(source_paragraph='「よし、いいぞ俺。伊達に妄想してねぇぜ。文明レベルの確認はまぁよし、とりあえず金は通用しない。ついでに店主と会話できたし意思の疎通も問題ない」', list_of_lines=['「よし、いいぞ俺。', '伊達に妄想してねぇぜ。', '文明レベルの確認はまぁよし、とりあえず金は通用しない。', 'ついでに店主と会話できたし意思の疎通も問題ない」。'], number_of_lines=4, list_of_clause_object_tuples=[(1, Clauses(source_line='「よし、いいぞ俺。', list_of_clauses=['「よし、', 'いいぞ俺。'], number_of_clauses=2)), (2, Clauses(source_line='伊達に妄想してねぇぜ。', list_of_clauses=['伊達に妄想してねぇぜ。'], number_of_clauses=1)), (3, Clauses(source_line='文明レベルの確認はまぁよし、とりあえず金は通用しない。', list_of_clauses=['文明レベルの確認はまぁよし、', 'とりあえず金は通用しない。'], number_of_clauses=2)), (4, Clauses(source_line='ついでに店主と会話できたし意思の疎通も問題ない」。', list_of_clauses=['ついでに店主と会話できたし意思の疎通も問題ない」。'], number_of_clauses=1))])), (37, Lines(source_paragraph='召喚されたと気付いて、スバルが最初に行ったのが『八百屋？』との交渉だった。店先に並んでいた『リンゴ？』を買おうとして、日本円を拒否されたのだ。', list_of_lines=['召喚されたと気付いて、スバルが最初に行ったのが『八百屋？』との交渉だった。', '店先に並んでいた『リンゴ？』を買おうとして、日本円を拒否されたのだ。'], number_of_lines=2, list_of_clause_object_tuples=[(1, Clauses(source_line='召喚されたと気付いて、スバルが最初に行ったのが『八百屋？』との交渉だった。', list_of_clauses=['召喚されたと気付いて、', 'スバルが最初に行ったのが『八百屋？』との交渉だった。'], number_of_clauses=2)), (2, Clauses(source_line='店先に並んでいた『リンゴ？』を買おうとして、日本円を拒否されたのだ。', list_of_clauses=['店先に並んでいた『リンゴ？』を買おうとして、', '日本円を拒否されたのだ。'], number_of_clauses=2))])), (38, Lines(source_paragraph='そのときに見た限りでは、この世界での通貨は金貨、銀貨、銅貨などらしい。貨幣自体が価値を持つ世界観の理解しやすさは、異世界ファンタジーらしいといえばらしい。', list_of_lines=['そのときに見た限りでは、この世界での通貨は金貨、銀貨、銅貨などらしい。', '貨幣自体が価値を持つ世界観の理解しやすさは、異世界ファンタジーらしいといえばらしい。'], number_of_lines=2, list_of_clause_object_tuples=[(1, Clauses(source_line='そのときに見た限りでは、この世界での通貨は金貨、銀貨、銅貨などらしい。', list_of_clauses=['そのときに見た限りでは、', 'この世界での通貨は金貨、', '銀貨、', '銅貨などらしい。'], number_of_clauses=4)), (2, Clauses(source_line='貨幣自体が価値を持つ世界観の理解しやすさは、異世界ファンタジーらしいといえばらしい。', list_of_clauses=['貨幣自体が価値を持つ世界観の理解しやすさは、', '異世界ファンタジーらしいといえばらしい。'], number_of_clauses=2))])), (39, Lines(source_paragraph='「まぁ、混じりもんとか粗悪品。五百ウォン硬貨みたいなの出てきて衰退するだろけど」', list_of_lines=['「まぁ、混じりもんとか粗悪品。', '五百ウォン硬貨みたいなの出てきて衰退するだろけど」。'], number_of_lines=2, list_of_clause_object_tuples=[(1, Clauses(source_line='「まぁ、混じりもんとか粗悪品。', list_of_clauses=['「まぁ、', '混じりもんとか粗悪品。'], number_of_clauses=2)), (2, Clauses(source_line='五百ウォン硬貨みたいなの出てきて衰退するだろけど」。', list_of_clauses=['五百ウォン硬貨みたいなの出てきて衰退するだろけど」。'], number_of_clauses=1))])), (40, Lines(source_paragraph='持ち歩くには重たすぎるしなぁ、と内心で呟き、再び通りをトカゲが引く馬車が通過。砂埃が盛大に舞っているが、行き交う人々は慣れているのか無頓着だ。', list_of_lines=['持ち歩くには重たすぎるしなぁ、と内心で呟き、再び通りをトカゲが引く馬車が通過。', '砂埃が盛大に舞っているが、行き交う人々は慣れているのか無頓着だ。'], number_of_lines=2, list_of_clause_object_tuples=[(1, Clauses(source_line='持ち歩くには重たすぎるしなぁ、と内心で呟き、再び通りをトカゲが引く馬車が通過。', list_of_clauses=['持ち歩くには重たすぎるしなぁ、', 'と内心で呟き、', '再び通りをトカゲが引く馬車が通過。'], number_of_clauses=3)), (2, Clauses(source_line='砂埃が盛大に舞っているが、行き交う人々は慣れているのか無頓着だ。', list_of_clauses=['砂埃が盛大に舞っているが、', '行き交う人々は慣れているのか無頓着だ。'], number_of_clauses=2))])), (41, Lines(source_paragraph='「それでも車に比べれば数は少ないか。……そういや、今のとこ犬とか猫も見てねぇな」', list_of_lines=['「それでも車に比べれば数は少ないか。', '……そういや、今のとこ犬とか猫も見てねぇな」。'], number_of_lines=2, list_of_clause_object_tuples=[(1, Clauses(source_line='「それでも車に比べれば数は少ないか。', list_of_clauses=['「それでも車に比べれば数は少ないか。'], number_of_clauses=1)), (2, Clauses(source_line='……そういや、今のとこ犬とか猫も見てねぇな」。', list_of_clauses=['……そういや、', '今のとこ犬とか猫も見てねぇな」。'], number_of_clauses=2))])), (42, Lines(source_paragraph='『馬車？』を引かせていた巨大なトカゲは、馬より一回りは大きかっただろうか。細身な分だけ全体的な質量は変わらなそうだが、爬虫類があれだけ大きいと違和感がスゴイ。', list_of_lines=['『馬車？』を引かせていた巨大なトカゲは、馬より一回りは大きかっただろうか。', '細身な分だけ全体的な質量は変わらなそうだが、爬虫類があれだけ大きいと違和感がスゴイ。'], number_of_lines=2, list_of_clause_object_tuples=[(1, Clauses(source_line='『馬車？』を引かせていた巨大なトカゲは、馬より一回りは大きかっただろうか。', list_of_clauses=['『馬車？』を引かせていた巨大なトカゲは、', '馬より一回りは大きかっただろうか。'], number_of_clauses=2)), (2, Clauses(source_line='細身な分だけ全体的な質量は変わらなそうだが、爬虫類があれだけ大きいと違和感がスゴイ。', list_of_clauses=['細身な分だけ全体的な質量は変わらなそうだが、', '爬虫類があれだけ大きいと違和感がスゴイ。'], number_of_clauses=2))])), (43, Lines(source_paragraph='「一般的……なんだろうな。トカゲも、人間の見た目も」', list_of_lines=['「一般的……なんだろうな。', 'トカゲも、人間の見た目も」。'], number_of_lines=2, list_of_clause_object_tuples=[(1, Clauses(source_line='「一般的……なんだろうな。', list_of_clauses=['「一般的……なんだろうな。'], number_of_clauses=1)), (2, Clauses(source_line='トカゲも、人間の見た目も」。', list_of_clauses=['トカゲも、', '人間の見た目も」。'], number_of_clauses=2))])), (44, Lines(source_paragraph='そして確認を最後に回した部分、この世界における人間の特殊な見た目だ。', list_of_lines=['そして確認を最後に回した部分、この世界における人間の特殊な見た目だ。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='そして確認を最後に回した部分、この世界における人間の特殊な見た目だ。', list_of_clauses=['そして確認を最後に回した部分、', 'この世界における人間の特殊な見た目だ。'], number_of_clauses=2))])), (45, Lines(source_paragraph='髪の色がカラフルなのは認める。染めれば基本的に何色の髪でもあり得るし、異世界ファンタジーな時点でそこは納得済みだ。', list_of_lines=['髪の色がカラフルなのは認める。', '染めれば基本的に何色の髪でもあり得るし、異世界ファンタジーな時点でそこは納得済みだ。'], number_of_lines=2, list_of_clause_object_tuples=[(1, Clauses(source_line='髪の色がカラフルなのは認める。', list_of_clauses=['髪の色がカラフルなのは認める。'], number_of_clauses=1)), (2, Clauses(source_line='染めれば基本的に何色の髪でもあり得るし、異世界ファンタジーな時点でそこは納得済みだ。', list_of_clauses=['染めれば基本的に何色の髪でもあり得るし、', '異世界ファンタジーな時点でそこは納得済みだ。'], number_of_clauses=2))])), (46, Lines(source_paragraph='問題視しているのは別の部分、たとえば『獣耳』だ。', list_of_lines=['問題視しているのは別の部分、たとえば『獣耳』だ。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='問題視しているのは別の部分、たとえば『獣耳』だ。', list_of_clauses=['問題視しているのは別の部分、', 'たとえば『獣耳』だ。'], number_of_clauses=2))])), (47, Lines(source_paragraph='ざっと見渡した限り、『イヌミミ』と『ネコミミ』は発見した。『バニー』もいれば、変わり種だと『リザードマン』っぽいのもチラッといたような気がする。', list_of_lines=['ざっと見渡した限り、『イヌミミ』と『ネコミミ』は発見した。', '『バニー』もいれば、変わり種だと『リザードマン』っぽいのもチラッといたような気がする。'], number_of_lines=2, list_of_clause_object_tuples=[(1, Clauses(source_line='ざっと見渡した限り、『イヌミミ』と『ネコミミ』は発見した。', list_of_clauses=['ざっと見渡した限り、', '『イヌミミ』と『ネコミミ』は発見した。'], number_of_clauses=2)), (2, Clauses(source_line='『バニー』もいれば、変わり種だと『リザードマン』っぽいのもチラッといたような気がする。', list_of_clauses=['『バニー』もいれば、', '変わり種だと『リザードマン』っぽいのもチラッといたような気がする。'], number_of_clauses=2))])), (48, Lines(source_paragraph='かと思えばスバルと変わらない見た目の人間もいるのだから、これらの結論は――、', list_of_lines=['かと思えばスバルと変わらない見た目の人間もいるのだから、これらの結論は――、'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='かと思えばスバルと変わらない見た目の人間もいるのだから、これらの結論は――、', list_of_clauses=['かと思えばスバルと変わらない見た目の人間もいるのだから、', 'これらの結論は――'], number_of_clauses=2))])), (49, Lines(source_paragraph='「ジャンルは異世界ファンタジー。文明は典型的な中世風。亜人ありありで、たぶん戦争とか冒険もありあり。動物に若干の違いはあるけど、役割的に変化なし――ってとこか」', list_of_lines=['「ジャンルは異世界ファンタジー。', '文明は典型的な中世風。', '亜人ありありで、たぶん戦争とか冒険もありあり。', '動物に若干の違いはあるけど、役割的に変化なし――ってとこか」。'], number_of_lines=4, list_of_clause_object_tuples=[(1, Clauses(source_line='「ジャンルは異世界ファンタジー。', list_of_clauses=['「ジャンルは異世界ファンタジー。'], number_of_clauses=1)), (2, Clauses(source_line='文明は典型的な中世風。', list_of_clauses=['文明は典型的な中世風。'], number_of_clauses=1)), (3, Clauses(source_line='亜人ありありで、たぶん戦争とか冒険もありあり。', list_of_clauses=['亜人ありありで、', 'たぶん戦争とか冒険もありあり。'], number_of_clauses=2)), (4, Clauses(source_line='動物に若干の違いはあるけど、役割的に変化なし――ってとこか」。', list_of_clauses=['動物に若干の違いはあるけど、', '役割的に変化なし――ってとこか」。'], number_of_clauses=2))])), (50, Lines(source_paragraph='それだけ整理して、スバルはため息とは違う長い息を吐く。', list_of_lines=['それだけ整理して、スバルはため息とは違う長い息を吐く。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='それだけ整理して、スバルはため息とは違う長い息を吐く。', list_of_clauses=['それだけ整理して、', 'スバルはため息とは違う長い息を吐く。'], number_of_clauses=2))])), (51, Lines(source_paragraph='自分の置かれた状況を口にしてみて、そのご都合主義的な展開に眉が寄る。', list_of_lines=['自分の置かれた状況を口にしてみて、そのご都合主義的な展開に眉が寄る。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='自分の置かれた状況を口にしてみて、そのご都合主義的な展開に眉が寄る。', list_of_clauses=['自分の置かれた状況を口にしてみて、', 'そのご都合主義的な展開に眉が寄る。'], number_of_clauses=2))])), (52, Lines(source_paragraph='妄想設定通りの展開なら、自分はこれから現代知識を駆使して『俺ＴＵＥＥ』を実行するはずだが、用意していた知識が使える世界観とは微妙に違う。', list_of_lines=['妄想設定通りの展開なら、自分はこれから現代知識を駆使して『俺ＴＵＥＥ』を実行するはずだが、用意していた知識が使える世界観とは微妙に違う。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='妄想設定通りの展開なら、自分はこれから現代知識を駆使して『俺ＴＵＥＥ』を実行するはずだが、用意していた知識が使える世界観とは微妙に違う。', list_of_clauses=['妄想設定通りの展開なら、', '自分はこれから現代知識を駆使して『俺ＴＵＥＥ』を実行するはずだが、', '用意していた知識が使える世界観とは微妙に違う。'], number_of_clauses=3))])), (53, Lines(source_paragraph='「過去の戦国時代に飛ばされた場合のシミュレーションは完璧だったんだけどな……戦国時代に飛ばされてたら、俺は信長に天下とらしてたぜ」', list_of_lines=['「過去の戦国時代に飛ばされた場合のシミュレーションは完璧だったんだけどな……戦国時代に飛ばされてたら、俺は信長に天下とらしてたぜ」'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='「過去の戦国時代に飛ばされた場合のシミュレーションは完璧だったんだけどな……戦国時代に飛ばされてたら、俺は信長に天下とらしてたぜ」', list_of_clauses=['「過去の戦国時代に飛ばされた場合のシミュレーションは完璧だったんだけどな……戦国時代に飛ばされてたら、', '俺は信長に天下とらしてたぜ」'], number_of_clauses=2))])), (54, Lines(source_paragraph='異世界ファンタジーだと、使える知識はせいぜい黒色火薬の配合率ぐらいか。', list_of_lines=['異世界ファンタジーだと、使える知識はせいぜい黒色火薬の配合率ぐらいか。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='異世界ファンタジーだと、使える知識はせいぜい黒色火薬の配合率ぐらいか。', list_of_clauses=['異世界ファンタジーだと、', '使える知識はせいぜい黒色火薬の配合率ぐらいか。'], number_of_clauses=2))])), (55, Lines(source_paragraph='それもこの世界の文明レベルによっては意味がない。異世界ファンタジーにつきものの『魔法』が存在する場合、それこそ火薬なんて花火程度の扱いだろう。', list_of_lines=['それもこの世界の文明レベルによっては意味がない。', '異世界ファンタジーにつきものの『魔法』が存在する場合、それこそ火薬なんて花火程度の扱いだろう。'], number_of_lines=2, list_of_clause_object_tuples=[(1, Clauses(source_line='それもこの世界の文明レベルによっては意味がない。', list_of_clauses=['それもこの世界の文明レベルによっては意味がない。'], number_of_clauses=1)), (2, Clauses(source_line='異世界ファンタジーにつきものの『魔法』が存在する場合、それこそ火薬なんて花火程度の扱いだろう。', list_of_clauses=['異世界ファンタジーにつきものの『魔法』が存在する場合、', 'それこそ火薬なんて花火程度の扱いだろう。'], number_of_clauses=2))])), (56, Lines(source_paragraph='「まぁ、魔法が万能なもんじゃないってのもある種のお約束か。もしも科学の発展とかに貢献できるチャンスがあるなら頑張るとして……さしあたっての問題は」', list_of_lines=['「まぁ、魔法が万能なもんじゃないってのもある種のお約束か。', 'もしも科学の発展とかに貢献できるチャンスがあるなら頑張るとして……さしあたっての問題は」。'], number_of_lines=2, list_of_clause_object_tuples=[(1, Clauses(source_line='「まぁ、魔法が万能なもんじゃないってのもある種のお約束か。', list_of_clauses=['「まぁ、', '魔法が万能なもんじゃないってのもある種のお約束か。'], number_of_clauses=2)), (2, Clauses(source_line='もしも科学の発展とかに貢献できるチャンスがあるなら頑張るとして……さしあたっての問題は」。', list_of_clauses=['もしも科学の発展とかに貢献できるチャンスがあるなら頑張るとして……さしあたっての問題は」。'], number_of_clauses=1))])), (57, Lines(source_paragraph='異世界召喚された原因も、目的もさっぱりわからないという点だ。', list_of_lines=['異世界召喚された原因も、目的もさっぱりわからないという点だ。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='異世界召喚された原因も、目的もさっぱりわからないという点だ。', list_of_clauses=['異世界召喚された原因も、', '目的もさっぱりわからないという点だ。'], number_of_clauses=2))])), (58, Lines(source_paragraph='召喚される前のことはよく覚えている。久々に家から出て、コンビニで夜食のカップラーメンを買って帰る途中だった。自転車の気分じゃなかったので徒歩で。', list_of_lines=['召喚される前のことはよく覚えている。', '久々に家から出て、コンビニで夜食のカップラーメンを買って帰る途中だった。', '自転車の気分じゃなかったので徒歩で。'], number_of_lines=3, list_of_clause_object_tuples=[(1, Clauses(source_line='召喚される前のことはよく覚えている。', list_of_clauses=['召喚される前のことはよく覚えている。'], number_of_clauses=1)), (2, Clauses(source_line='久々に家から出て、コンビニで夜食のカップラーメンを買って帰る途中だった。', list_of_clauses=['久々に家から出て、', 'コンビニで夜食のカップラーメンを買って帰る途中だった。'], number_of_clauses=2)), (3, Clauses(source_line='自転車の気分じゃなかったので徒歩で。', list_of_clauses=['自転車の気分じゃなかったので徒歩で。'], number_of_clauses=1))])), (59, Lines(source_paragraph='そしてその途中、ふと夜空を見上げて『今夜は満月一歩手前だな』と思ったことまで覚えている。', list_of_lines=['そしてその途中、ふと夜空を見上げて『今夜は満月一歩手前だな』と思ったことまで覚えている。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='そしてその途中、ふと夜空を見上げて『今夜は満月一歩手前だな』と思ったことまで覚えている。', list_of_clauses=['そしてその途中、', 'ふと夜空を見上げて『今夜は満月一歩手前だな』と思ったことまで覚えている。'], number_of_clauses=2))])), (60, Lines(source_paragraph='それから視線を下げてまばたきをしたら、いつの間にか昼だった。', list_of_lines=['それから視線を下げてまばたきをしたら、いつの間にか昼だった。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='それから視線を下げてまばたきをしたら、いつの間にか昼だった。', list_of_clauses=['それから視線を下げてまばたきをしたら、', 'いつの間にか昼だった。'], number_of_clauses=2))])), (61, Lines(source_paragraph='夜から一瞬で昼だ。', list_of_lines=['夜から一瞬で昼だ。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='夜から一瞬で昼だ。', list_of_clauses=['夜から一瞬で昼だ。'], number_of_clauses=1))])), (62, Lines(source_paragraph='異常事態が起きたのはすぐにわかった。それしかわからなかったが。', list_of_lines=['異常事態が起きたのはすぐにわかった。', 'それしかわからなかったが。'], number_of_lines=2, list_of_clause_object_tuples=[(1, Clauses(source_line='異常事態が起きたのはすぐにわかった。', list_of_clauses=['異常事態が起きたのはすぐにわかった。'], number_of_clauses=1)), (2, Clauses(source_line='それしかわからなかったが。', list_of_clauses=['それしかわからなかったが。'], number_of_clauses=1))])), (63, Lines(source_paragraph='今でこそ落ち着いているが、その直後の慌てぶりときたら子々孫々まで語り継がれるべきヘタレぶりである。', list_of_lines=['今でこそ落ち着いているが、その直後の慌てぶりときたら子々孫々まで語り継がれるべきヘタレぶりである。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='今でこそ落ち着いているが、その直後の慌てぶりときたら子々孫々まで語り継がれるべきヘタレぶりである。', list_of_clauses=['今でこそ落ち着いているが、', 'その直後の慌てぶりときたら子々孫々まで語り継がれるべきヘタレぶりである。'], number_of_clauses=2))])), (64, Lines(source_paragraph='「まぁ、長男の俺が消息不明なら子々孫々もクソもないけど」', list_of_lines=['「まぁ、長男の俺が消息不明なら子々孫々もクソもないけど」'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='「まぁ、長男の俺が消息不明なら子々孫々もクソもないけど」', list_of_clauses=['「まぁ、', '長男の俺が消息不明なら子々孫々もクソもないけど」'], number_of_clauses=2))])), (65, Lines(source_paragraph='呟きながら、改めてスバルは自分の所有物を確認。', list_of_lines=['呟きながら、改めてスバルは自分の所有物を確認。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='呟きながら、改めてスバルは自分の所有物を確認。', list_of_clauses=['呟きながら、', '改めてスバルは自分の所有物を確認。'], number_of_clauses=2))])), (66, Lines(source_paragraph='異世界ファンタジーの現状では初期装備が想像以上に重要だ。今はどれだけ細い糸であっても繋がっている事実が大事。', list_of_lines=['異世界ファンタジーの現状では初期装備が想像以上に重要だ。', '今はどれだけ細い糸であっても繋がっている事実が大事。'], number_of_lines=2, list_of_clause_object_tuples=[(1, Clauses(source_line='異世界ファンタジーの現状では初期装備が想像以上に重要だ。', list_of_clauses=['異世界ファンタジーの現状では初期装備が想像以上に重要だ。'], number_of_clauses=1)), (2, Clauses(source_line='今はどれだけ細い糸であっても繋がっている事実が大事。', list_of_clauses=['今はどれだけ細い糸であっても繋がっている事実が大事。'], number_of_clauses=1))])), (67, Lines(source_paragraph='まずケータイ（電池切れそう）、財布（レンタルビデオ屋の会員証多数）、コンビニで買ったカップラーメン（とんこつ醤油味）、同じくスナック菓子（コーンポタージュ味）、愛着しているグレーのジャージ（未洗濯）、使い古したスニーカー（二年もの）、以上だ。', list_of_lines=['まずケータイ（電池切れそう）、財布（レンタルビデオ屋の会員証多数）、コンビニで買ったカップラーメン（とんこつ醤油味）、同じくスナック菓子（コーンポタージュ味）、愛着しているグレーのジャージ（未洗濯）、使い古したスニーカー（二年もの）、以上だ。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='まずケータイ（電池切れそう）、財布（レンタルビデオ屋の会員証多数）、コンビニで買ったカップラーメン（とんこつ醤油味）、同じくスナック菓子（コーンポタージュ味）、愛着しているグレーのジャージ（未洗濯）、使い古したスニーカー（二年もの）、以上だ。', list_of_clauses=['まずケータイ（電池切れそう）、', '財布（レンタルビデオ屋の会員証多数）、', 'コンビニで買ったカップラーメン（とんこつ醤油味）、', '同じくスナック菓子（コーンポタージュ味）、', '愛着しているグレーのジャージ（未洗濯）、', '使い古したスニーカー（二年もの）、', '以上だ。'], number_of_clauses=7))])), (68, Lines(source_paragraph='「終わったな……なんで俺はピストルのひとつでも持ってねぇんだ。どーしろと」', list_of_lines=['「終わったな……なんで俺はピストルのひとつでも持ってねぇんだ。', 'どーしろと」。'], number_of_lines=2, list_of_clause_object_tuples=[(1, Clauses(source_line='「終わったな……なんで俺はピストルのひとつでも持ってねぇんだ。', list_of_clauses=['「終わったな……なんで俺はピストルのひとつでも持ってねぇんだ。'], number_of_clauses=1)), (2, Clauses(source_line='どーしろと」。', list_of_clauses=['どーしろと」。'], number_of_clauses=1))])), (69, Lines(source_paragraph='役立つのは腹の足しになりそうなお菓子ぐらいか。小腹を救って終了だが。', list_of_lines=['役立つのは腹の足しになりそうなお菓子ぐらいか。', '小腹を救って終了だが。'], number_of_lines=2, list_of_clause_object_tuples=[(1, Clauses(source_line='役立つのは腹の足しになりそうなお菓子ぐらいか。', list_of_clauses=['役立つのは腹の足しになりそうなお菓子ぐらいか。'], number_of_clauses=1)), (2, Clauses(source_line='小腹を救って終了だが。', list_of_clauses=['小腹を救って終了だが。'], number_of_clauses=1))])), (70, Lines(source_paragraph='「事態は絶望的。そしてやっぱり原因は不明。鏡くぐった覚えも池に落ちた記憶もないし、何より召喚ものなら俺を召喚した美少女どこだよ」', list_of_lines=['「事態は絶望的。', 'そしてやっぱり原因は不明。', '鏡くぐった覚えも池に落ちた記憶もないし、何より召喚ものなら俺を召喚した美少女どこだよ」。'], number_of_lines=3, list_of_clause_object_tuples=[(1, Clauses(source_line='「事態は絶望的。', list_of_clauses=['「事態は絶望的。'], number_of_clauses=1)), (2, Clauses(source_line='そしてやっぱり原因は不明。', list_of_clauses=['そしてやっぱり原因は不明。'], number_of_clauses=1)), (3, Clauses(source_line='鏡くぐった覚えも池に落ちた記憶もないし、何より召喚ものなら俺を召喚した美少女どこだよ」。', list_of_clauses=['鏡くぐった覚えも池に落ちた記憶もないし、', '何より召喚ものなら俺を召喚した美少女どこだよ」。'], number_of_clauses=2))])), (71, Lines(source_paragraph='いわばメインヒロインの不在。二次元の世界からすればあり得ない職務怠慢だ。', list_of_lines=['いわばメインヒロインの不在。', '二次元の世界からすればあり得ない職務怠慢だ。'], number_of_lines=2, list_of_clause_object_tuples=[(1, Clauses(source_line='いわばメインヒロインの不在。', list_of_clauses=['いわばメインヒロインの不在。'], number_of_clauses=1)), (2, Clauses(source_line='二次元の世界からすればあり得ない職務怠慢だ。', list_of_clauses=['二次元の世界からすればあり得ない職務怠慢だ。'], number_of_clauses=1))])), (72, Lines(source_paragraph='召喚しておいて無目的で放置されたとあっては、やり捨てされたようなものである。', list_of_lines=['召喚しておいて無目的で放置されたとあっては、やり捨てされたようなものである。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='召喚しておいて無目的で放置されたとあっては、やり捨てされたようなものである。', list_of_clauses=['召喚しておいて無目的で放置されたとあっては、', 'やり捨てされたようなものである。'], number_of_clauses=2))])), (73, Lines(source_paragraph='実際、現状確認すら終わったスバルは現実逃避すらできずにうなだれるしかない。', list_of_lines=['実際、現状確認すら終わったスバルは現実逃避すらできずにうなだれるしかない。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='実際、現状確認すら終わったスバルは現実逃避すらできずにうなだれるしかない。', list_of_clauses=['実際、', '現状確認すら終わったスバルは現実逃避すらできずにうなだれるしかない。'], number_of_clauses=2))])), (74, Lines(source_paragraph='「マジで勘弁してくれよ。俺にどうしろっつーんだよ」', list_of_lines=['「マジで勘弁してくれよ。', '俺にどうしろっつーんだよ」。'], number_of_lines=2, list_of_clause_object_tuples=[(1, Clauses(source_line='「マジで勘弁してくれよ。', list_of_clauses=['「マジで勘弁してくれよ。'], number_of_clauses=1)), (2, Clauses(source_line='俺にどうしろっつーんだよ」。', list_of_clauses=['俺にどうしろっつーんだよ」。'], number_of_clauses=1))])), (75, Lines(source_paragraph='弱音、泣き言がこぼれて早くも折れそうだ。帰りたい、とひたすら思う。', list_of_lines=['弱音、泣き言がこぼれて早くも折れそうだ。', '帰りたい、とひたすら思う。'], number_of_lines=2, list_of_clause_object_tuples=[(1, Clauses(source_line='弱音、泣き言がこぼれて早くも折れそうだ。', list_of_clauses=['弱音、', '泣き言がこぼれて早くも折れそうだ。'], number_of_clauses=2)), (2, Clauses(source_line='帰りたい、とひたすら思う。', list_of_clauses=['帰りたい、', 'とひたすら思う。'], number_of_clauses=2))])), (76, Lines(source_paragraph='妄想は妄想のままでよかった。異世界召喚なんてものは頭の中で無双して俺ＴＵＥＥするのが楽しいんであって、本当に放り込まれたら尻ごみ以外の何ができる。', list_of_lines=['妄想は妄想のままでよかった。', '異世界召喚なんてものは頭の中で無双して俺ＴＵＥＥするのが楽しいんであって、本当に放り込まれたら尻ごみ以外の何ができる。'], number_of_lines=2, list_of_clause_object_tuples=[(1, Clauses(source_line='妄想は妄想のままでよかった。', list_of_clauses=['妄想は妄想のままでよかった。'], number_of_clauses=1)), (2, Clauses(source_line='異世界召喚なんてものは頭の中で無双して俺ＴＵＥＥするのが楽しいんであって、本当に放り込まれたら尻ごみ以外の何ができる。', list_of_clauses=['異世界召喚なんてものは頭の中で無双して俺ＴＵＥＥするのが楽しいんであって、', '本当に放り込まれたら尻ごみ以外の何ができる。'], number_of_clauses=2))])), (77, Lines(source_paragraph='「とにかく当面は生きるのが目的だが……コミュレベル１の俺でやってけるのか？」', list_of_lines=['「とにかく当面は生きるのが目的だが……コミュレベル１の俺でやってけるのか？」'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='「とにかく当面は生きるのが目的だが……コミュレベル１の俺でやってけるのか？」', list_of_clauses=['「とにかく当面は生きるのが目的だが……コミュレベル１の俺でやってけるのか？」'], number_of_clauses=1))])), (78, Lines(source_paragraph='まともに誰かと会話するなど、家族を除けばコンビニの店員ぐらいしかいない。そんな生活を一年近く続けてきたのだ。距離の測り方なんてとうに忘れている。', list_of_lines=['まともに誰かと会話するなど、家族を除けばコンビニの店員ぐらいしかいない。', 'そんな生活を一年近く続けてきたのだ。', '距離の測り方なんてとうに忘れている。'], number_of_lines=3, list_of_clause_object_tuples=[(1, Clauses(source_line='まともに誰かと会話するなど、家族を除けばコンビニの店員ぐらいしかいない。', list_of_clauses=['まともに誰かと会話するなど、', '家族を除けばコンビニの店員ぐらいしかいない。'], number_of_clauses=2)), (2, Clauses(source_line='そんな生活を一年近く続けてきたのだ。', list_of_clauses=['そんな生活を一年近く続けてきたのだ。'], number_of_clauses=1)), (3, Clauses(source_line='距離の測り方なんてとうに忘れている。', list_of_clauses=['距離の測り方なんてとうに忘れている。'], number_of_clauses=1))])), (79, Lines(source_paragraph='「チャットなら喋るのと変わらないスピードでタイプできんのに……」', list_of_lines=['「チャットなら喋るのと変わらないスピードでタイプできんのに……」'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='「チャットなら喋るのと変わらないスピードでタイプできんのに……」', list_of_clauses=['「チャットなら喋るのと変わらないスピードでタイプできんのに……」'], number_of_clauses=1))])), (80, Lines(source_paragraph='指をわきわきさせながら今後を不安がるスバル。', list_of_lines=['指をわきわきさせながら今後を不安がるスバル。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='指をわきわきさせながら今後を不安がるスバル。', list_of_clauses=['指をわきわきさせながら今後を不安がるスバル。'], number_of_clauses=1))])), (81, Lines(source_paragraph='と、その表情が変わる。理由は音だ。', list_of_lines=['と、その表情が変わる。', '理由は音だ。'], number_of_lines=2, list_of_clause_object_tuples=[(1, Clauses(source_line='と、その表情が変わる。', list_of_clauses=['と、', 'その表情が変わる。'], number_of_clauses=2)), (2, Clauses(source_line='理由は音だ。', list_of_clauses=['理由は音だ。'], number_of_clauses=1))])), (82, Lines(source_paragraph='ふいに路地裏に響いた足音――見れば路地の入口、三人ほどの男が道を塞ぐように立っていた。', list_of_lines=['ふいに路地裏に響いた足音――見れば路地の入口、三人ほどの男が道を塞ぐように立っていた。'], number_of_lines=1, list_of_clause_object_tuples=[(1, Clauses(source_line='ふいに路地裏に響いた足音――見れば路地の入口、三人ほどの男が道を塞ぐように立っていた。', list_of_clauses=['ふいに路地裏に響いた足音――見れば路地の入口、', '三人ほどの男が道を塞ぐように立っていた。'], number_of_clauses=2))]))]
