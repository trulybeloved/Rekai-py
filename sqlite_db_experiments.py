import sqlite3

db_connnection = sqlite3.connect('experiment_db.db')

cursor = db_connnection.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS table1 (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)''')


cursor.execute('''CREATE TABLE IF NOT EXISTS table2 (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)''')


cursor.execute('''CREATE TABLE IF NOT EXISTS table3 (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)''')





cursor.execute('INSERT INTO table1 (id, name, age) VALUES (?, ?, ?)', (1, 'John Doe', 25))
cursor.execute('INSERT INTO table1 (id, name, age) VALUES (?, ?, ?)', (2, 'John Doe2', 256))
cursor.execute('INSERT INTO table1 (id, name, age) VALUES (?, ?, ?)', (3, 'John Doe3', 125))
cursor.execute('INSERT INTO table1 (id, name, age) VALUES (?, ?, ?)', (4, 'John Doe4', 425))
cursor.execute('INSERT INTO table1 (id, name, age) VALUES (?, ?, ?)', (5, 'John Doe5', 725))
cursor.execute('INSERT INTO table1 (id, name, age) VALUES (?, ?, ?)', (6, 'John Doe6', 125))


entry = cursor.execute("SELECT * from table1")

print(entry)

row = cursor.fetchall()
print(row)

cursor.close()
db_connnection.close()









