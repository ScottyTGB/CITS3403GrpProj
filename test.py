import sqlite3

conn = sqlite3.connect('user.db') 
conn.execute('CREATE TABLE students (userID TEXT, userName TEXT, userEmail TEXT, userPassword TEXT)') 
conn.close()  

conn = sqlite3.connect('tutor.db') 
conn.execute('CREATE TABLE tutor (tutorID TEXT, tutorName TEXT, tutorEmail TEXT)') 
conn.close()  

conn = sqlite3.connect('request.db') 
conn.execute('CREATE TABLE request (requestID TEXT, userID TEXT, tutorID TEXT, unit TEXT)') 
conn.close() 