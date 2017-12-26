import sqlite3

conn = sqlite3.connect('database.db')
print('Database Created !!')

conn.execute('create table users (name text, age text, phone text unique, email text primary key, pass text)')
print('Table Created')
conn.close()