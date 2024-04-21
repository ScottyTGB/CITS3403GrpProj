from flask import Flask
from flask import render_template, request
import sqlite3

app = Flask(__name__)
app.config["DATABASE"] = "database.db"

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
        un = request.form['uniname']
        lecturer = request.form['lecturer']
        outline = request.form['outline']
        opensemester = request.form['opensemester']
        with sqlite3.connect("database.db") as con:  
           cur = con.cursor()    
           cur.execute("INSERT INTO students (un,lecturer,outline,opensemester) VALUES (?,?,?,?)",(un,lecturer,outline,opensemester) )    
           con.commit()     
           msg = "success"
    except:
        con.rollback()    
        msg = "failed"
    finally:
        return render_template("result.html",msg = msg) 
        # con.close()    

# show the result from database
@app.route('/show')
def show_student():
    con = sqlite3.connect("database.db")  
    con.row_factory = sqlite3.Row     
    cur = con.cursor()        
    cur.execute("select * from students")   
    rows = cur.fetchall()      
    return render_template("show.html",rows = rows)  

if __name__ == "__main__":
    app.run()
