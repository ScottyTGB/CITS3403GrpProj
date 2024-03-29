import sqlite3

import re

def is_valid_email(email):
  email_regex = r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$"
  return re.match(email_regex, email) is not None




connection = sqlite3.connect("FormDatabase.db")
cursor = connection.cursor()

def insert_UserData(email, passwordHash):
    if(is_valid_email(email)):
        cursor.execute("INSERT into Users (Email, PasswordHash) VALUES (?,?)", (email, passwordHash))
        connection.commit()
    else:
        print("Email not Valid")

def view_data(table):
    cursor.execute(f"SELECT * FROM {table}")
    print(cursor.fetchall())

def insert_manyUserData(userList):
    cursor.executemany("INSERT into Users (Email, PasswordHash) VALUES (?,?)", userList)
    connection.commit()

#cursor.execute("CREATE TABLE Users( ID INTEGER PRIMARY KEY AUTOINCREMENT, Email VARCHAR(255) NOT NULL UNIQUE, PasswordHash CHAR(64) NOT NULL)")


insert_UserData("helloooo@gmail.com","Passowrd")
view_data("Users")

connection.close()
