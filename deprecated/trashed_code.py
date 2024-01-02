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

