from flask import Flask
from flask import render_template, request
import sqlite3

app = Flask(__name__)
app.config["DATABASE"] = "user.db"
app.config["DATABASE"] = "tutor.db"

def get_db():
    db = sqlite3.connect(app.config["DATABASE"])
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource("schema.sql",mode = 'r') as f:
            db.cursor().executescript(f.read())
        db.commit()
 

@app.route("/",methods = ['POST', 'GET'])
def create_student():
    return render_template('uni.html') 

@app.route('/addstudent',methods = ['POST', 'GET'])
def add_student():
    try:
        #request for data
        userID = request.form['userID']
        userName = request.form['userName']
        userEmail = request.form['userEmail']
        userPassword = request.form['userPassword']
        with sqlite3.connect("user.db") as con_students:  
           cur_students = con_students.cursor()    
           cur_students.execute("INSERT INTO students (userID,userName,userEmail,userPassword) VALUES (?,?,?,?)",(userID,userName,userEmail,userPassword) )    
           con_students.commit()     
           msg = "success"
    except:
        con_students.rollback()    
        msg = "failed"
    finally:
        return render_template("result.html",msg = msg) 
        # con.close()   


@app.route('/addtutor',methods = ['POST', 'GET'])
def add_tutor():
    try:
        #request for data
        tutorID = request.form['tutorID']
        tutorName = request.form['tutorName']
        tutorEmail = request.form['tutorEmail']
        with sqlite3.connect("tutor.db") as con_tutors:  
           cur_tutors = con_tutors.cursor()    
           cur_tutors.execute("INSERT INTO tutor (tutorID,tutorName,tutorEmail) VALUES (?,?,?)",(tutorID,tutorName,tutorEmail) )    
           con_tutors.commit()     
           msg = "success"
    except:
        con_tutors.rollback()    
        msg = "failed"
    finally:      
        return render_template("result.html",msg = msg) 
    

@app.route('/addrequest',methods = ['POST', 'GET'])
def add_request():
    try:
        #request for data
        requestID = request.form['requestID']
        userID = request.form['userID']
        tutorID = request.form['tutorID']
        unit = request.form['unit']
        with sqlite3.connect("request.db") as con_request:  
           cur_request = con_request.cursor()    
           cur_request.execute("INSERT INTO request (requestID,userID,tutorID,unit) VALUES (?,?,?,?)",(requestID,userID,tutorID,unit) )    
           con_request.commit()     
           msg = "success"
    except:
        con_request.rollback()    
        msg = "failed"
    finally:      
        return render_template("result.html",msg = msg) 



# show the result from database
@app.route('/show')
def show_student():
    # Connect to the students database
    con_students = sqlite3.connect("user.db")  
    con_students.row_factory = sqlite3.Row     
    cur_students = con_students.cursor()        
    cur_students.execute("select * from students")   
    rows_students = cur_students.fetchall()      
    
    # Connect to the tutors database
    con_tutors = sqlite3.connect("tutor.db")
    con_tutors.row_factory = sqlite3.Row
    cur_tutors = con_tutors.cursor()
    cur_tutors.execute("select * from tutor")
    rows_tutors = cur_tutors.fetchall()

    # Connect to the request database
    con_request = sqlite3.connect("request.db")
    con_request.row_factory = sqlite3.Row
    cur_request = con_request.cursor()
    cur_request.execute("select * from request")
    rows_request = cur_request.fetchall()
    
    # Close both connections
    con_students.close()
    con_tutors.close()
    con_request.close()

    return render_template("show.html", rows_students=rows_students, rows_tutors=rows_tutors, rows_request=rows_request)
  

if __name__ == "__main__":
    app.run()
