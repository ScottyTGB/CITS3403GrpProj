import sqlite3


con_students = sqlite3.connect("user.db")  
cur_students = con_students.cursor()        
cur_students.execute("select * from user")   
for row in cur_students.fetchall():
  print([str(value) for value in row])

con_requests = sqlite3.connect("request.db")  
cur_requests = con_requests.cursor()        
cur_requests.execute("select * from request")   
for row in cur_requests.fetchall():
  print([str(value) for value in row])
