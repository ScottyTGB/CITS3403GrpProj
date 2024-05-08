import sqlite3


def create_user_table():
    conn = sqlite3.connect('user.db') 
    conn.execute('CREATE TABLE user (userID INTEGER PRIMARY KEY, userEmail TEXT, userPassword TEXT)') 
    conn.close()  
def create_tutor_table():
    conn = sqlite3.connect('tutor.db') 
    conn.execute('CREATE TABLE tutor (tutorID INTEGER PRIMARY KEY, tutorEmail TEXT)') 
    conn.close()  
def create_request_table():
    conn = sqlite3.connect('request.db') 
    conn.execute('CREATE TABLE request (requestID INTEGER PRIMARY KEY, userID TEXT, tutorID TEXT, unit TEXT)') 
    conn.close() 