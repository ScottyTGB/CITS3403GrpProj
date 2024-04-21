import sqlite3

conn = sqlite3.connect('database.db') 
conn.execute('CREATE TABLE students (un TEXT, lecturer TEXT, outline TEXT, opensemester TEXT)') 
conn.close()       