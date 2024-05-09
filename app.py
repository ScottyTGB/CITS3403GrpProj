from flask import Flask, flash, redirect, render_template, request, session, abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import initdb 
import os
#TODO
#Add in remember me cookie
#Change all routes to be if statements rather than seperate route methods
#SQLalchemy security stuff
#Flash doesn't work?

#Find and set secret key, start app
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
env_path = os.path.join('.config', 'config.env')

if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            key, value = line.strip().split('=')
            os.environ[key] = value


app = Flask(__name__)

app.config['SECRET_KEY'] = secret_key = os.environ.get('SECRET_KEY')

app.config["DATABASE"] = "user.db"
app.config["DATABASE"] = "tutor.db"
app.config["DATABASE"] = "request.db"
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Create user, request and login manager
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):

    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

class Request:

    def __init__(self, id, requestor, tutor, unit):
        self.id = id
        self.requestor = requestor
        self.tutor = tutor
        self.unit = unit

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Helper functions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def hash_pass(password):
    return generate_password_hash(password)

def check_hash(hash,password):
    return check_password_hash(hash,password)

def get_requests():
    requests_array = []
    con_requests = sqlite3.connect("request.db")
    cur_requests = con_requests.cursor()
    cur_requests.execute("select * from user")
    for row in cur_requests.fetchall():
        requests_array.append([str(value) for value in row])
    return(requests_array)

def load_request(requestID):
    requests_dict = {}
    request_db = get_requests()
    for request in request_db:
        requests_dict[request[0]] = Request(*request)
    return requests_dict.get(requestID)

def get_users():
    user_array = []
    con_students = sqlite3.connect("user.db")  
    cur_students = con_students.cursor()        
    cur_students.execute("select * from user")   
    for row in cur_students.fetchall():
        user_array.append([str(value) for value in row])
    return(user_array)

def get_user_by_id(userID):
    con_students = sqlite3.connect("user.db")  
    cur_students = con_students.cursor()        
    cur_students.execute(f"select * from user where userID = {userID}")   
    
    return(cur_students.fetchall())    

@login_manager.user_loader
def load_user(username):
    user_dict = {}
    users_in_db = get_users()
    for user_data in users_in_db:
        user_dict[user_data[1]] = User(*user_data)

    return user_dict.get(username)
  

def check_databases():
    dbs = ["request.db","tutor.db","user.db"]
    for db in dbs:
        if not (os.path.isfile(db)):
            match db:
                case "request.db":
                    initdb.create_request_table()
                case "tutor.db":
                    initdb.create_tutor_table()
                case "user.db":
                    initdb.create_user_table()

def get_db():
    db = sqlite3.connect(app.config["DATABASE"])
    db.row_factory = sqlite3.Row
    return db

#Testing user
@app.route('/profile')
def profile():
    print(session['user'])
    if (session['user']):
        return f"Welcome {session['user']}"
    return f"error"
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Create Request route
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route('/createrequest', methods=["GET","POST"])
def create_request():
    if request.method == "GET":
        return render_template("createrequest.html")
    elif request.method == "POST":
        unit = request.form['unit']
        print(unit)
        requestor = session['userID']
        if(requestor and unit):
            try:
                with sqlite3.connect("request.db") as con_user:  
                    cur_user = con_user.cursor()
                    cur_user.execute("INSERT INTO request (userID,tutorID,unit) VALUES (?,?,?)",(requestor,None,unit))    
                    con_user.commit()
            except:
                con_user.rollback()
                flash("Eror entering request to database")
        else:
            flash("Enter valid unit name")
        return redirect('/requests')    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Requests route
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route('/requests', methods=["GET","POST"])
def view_requests():
    if request.method == "GET":
        requests = []
        con_requests = sqlite3.connect("request.db")  
        cur_requests = con_requests.cursor()        
        cur_requests.execute("select * from request")   
        for row in cur_requests.fetchall():
            requests.append([str(value) for value in row])
        users_requesting = []
        request_strings = []
        for request_info in requests:
            users_requesting.append(get_user_by_id(request_info[1]))
            request_strings.append(f"{users_requesting} has requested tutoring in {request_info[3]}")
        print(users_requesting[0])
        return render_template("requests.html",data=request_strings)
    elif request.method == "POST":
        #When tutor clicks accept
        #Need to be able to get details of request from table, HTML will have ID, call by ID and then check if requestor and tutor ID are the same if so then fail
        #Get requestID from HTML
        requestID = None
        requestPicked = load_request(requestID)
        tutor = session['userID']
        if(tutor == requestPicked.requestor):
            flash("Cannot accept own request")
        if(tutor):
            try:
                with sqlite3.connect("request.db") as con_user:  
                    cur_user = con_user.cursor()    
                    #Change this to be an update clause updatign the value of tutorID to sessionID
                    #cur_user.execute("INSERT INTO request (userID,tutorID,unit) VALUES (?,?,?)",(requestor,None,unit))    
                    con_user.commit()
            except:
                con_user.rollback()
                flash("Eror entering request to database")            

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Home route
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route('/')
def sendhome():
    return redirect("/home")

@app.route('/home')
def home():
    return render_template('index.html')
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Login route
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']
    
    user = load_user(username)
    
    if user and check_hash(user.password,password):
        login_user(user)
        session['user'] = username
        print(user.id)
        session['userID'] = user.id
        print(session['user'])
        return redirect('/home')
    else:
        return 'Invalid username or password'       

@app.route('/login', methods=['GET'])
def load_login():
    return render_template("login.html")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Register route
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
@app.route('/register', methods=['GET'])
def load_register():
    return render_template("register.html")

@app.route('/register', methods=['POST'])
def do_register():
    username = request.form['username']
    password = request.form['password']
    user = load_user(username)
    if user:
        flash("Username already taken")
        #Create login button for user to move to login
    elif(username and password):
        hashed = hash_pass(password)
        try:
            with sqlite3.connect("user.db") as con_user:  
                cur_user = con_user.cursor()    
                cur_user.execute("INSERT INTO user (userEmail,userPassword) VALUES (?,?)",(username,hashed))    
                con_user.commit()
            do_login()                     
        except:
            con_user.rollback()
            flash("Eror entering user to database")
    else:
        flash("Enter valid username and password")
    return redirect('/home')
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Logout route
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return home()
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Main
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
if __name__ == "__main__":
    check_databases()
    app.secret_key = os.urandom(12)
    app.run(debug=True,port=4000)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~