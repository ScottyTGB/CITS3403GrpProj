from flask import Flask, flash, redirect, render_template, request, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from initdb import db, User, Tutor, Request
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

# app.config["DATABASE"] = "user.db"
# app.config["DATABASE"] = "tutor.db"
# app.config["DATABASE"] = "request.db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Create user, request and login manager
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
login_manager = LoginManager()
login_manager.init_app(app)

# class User(UserMixin):

#     def __init__(self, id, username, password):
#         self.id = id
#         self.username = username
#         self.password = password

# class Request:

#     def __init__(self, id, requestor, tutor, unit):
#         self.id = id
#         self.requestor = requestor
#         self.tutor = tutor
#         self.unit = unit
class UserModel(UserMixin, User):
    pass
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Helper functions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def hash_pass(password):
    return generate_password_hash(password)

def check_hash(hash,password):
    return check_password_hash(hash,password)

def get_requests():
    return Request.query.all()

def load_request(requestID):
    return Request.query.get(requestID)

def get_users():
    return User.query.all()

def get_user_by_id(userID):
    return User.query.get(userID)
    

# @login_manager.user_loader
# def load_user(username):
#     user_dict = {}
#     users_in_db = get_users()
#     for user_data in users_in_db:
#         user_dict[user_data[1]] = User(*user_data)

#     return user_dict.get(username)
@login_manager.user_loader
def load_user(userID):
    return UserModel.query.get(int(userID))

def check_databases():
    with app.app_context():
        db.create_all()

# def get_db():
#     db = sqlite3.connect(app.config["DATABASE"])
#     db.row_factory = sqlite3.Row
#     return db

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
@login_required
def create_request():
    if request.method == "GET":
        return render_template("createrequest.html")
    elif request.method == "POST":
        unit = request.form['unit']
        requestor = session['userID']
        if requestor and unit:
            try:
                new_request = Request(userID=requestor, tutorID=None, unit=unit)
                db.session.add(new_request)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash("Error entering request to database: " + str(e))
        else:
            flash("Enter valid unit name")
        return redirect('/requests')    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Requests route
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route('/requests', methods=["GET","POST"])
# def view_requests():
#     if request.method == "GET":
#         requests = []
#         con_requests = sqlite3.connect("request.db")  
#         cur_requests = con_requests.cursor()        
#         cur_requests.execute("select * from request")   
#         for row in cur_requests.fetchall():
#             requests.append([str(value) for value in row])
#         request_strings = []
#         for request_info in requests:
#             if(request_info != []):
#                 print(request_info)
#                 user_requesting = get_user_by_id(request_info[1])
#                 print(user_requesting)
#                 request_strings.append(f"{list(user_requesting[0])[1]} has requested tutoring in {request_info[3]}")
#         print(user_requesting[0][1])
#         print()
#         return render_template("requests.html",data=request_strings)
#     elif request.method == "POST":
#         #When tutor clicks accept
#         #Need to be able to get details of request from table, HTML will have ID, call by ID and then check if requestor and tutor ID are the same if so then fail
#         #Get requestID from HTML
#         requestID = None
#         requestPicked = load_request(requestID)
#         tutor = session['userID']
#         print(tutor)
#         if(tutor == requestPicked.requestor):
#             flash("Cannot accept own request")
#         if(tutor):
#             try:
#                 with sqlite3.connect("request.db") as con_user:  
#                     cur_user = con_user.cursor()    
#                     #Change this to be an update clause updatign the value of tutorID to sessionID
#                     #cur_user.execute("INSERT INTO request (userID,tutorID,unit) VALUES (?,?,?)",(requestor,None,unit))    
#                     con_user.commit()
#             except:
#                 con_user.rollback()
#                 flash("Eror entering request to database")            
@login_required
def view_requests():
    if request.method == "GET":
        requests = get_requests()
        request_strings = []
        for request_info in requests:
            user_requesting = get_user_by_id(request_info.userID)
            request_strings.append(f"{user_requesting.userEmail} has requested tutoring in {request_info.unit}")
        return render_template("requests.html", data=request_strings)
    elif request.method == "POST":
        requestID = request.form.get('requestID')
        requestPicked = load_request(requestID)
        tutor = session['userID']
        if tutor == requestPicked.userID:
            flash("Cannot accept own request")
        else:
            try:
                requestPicked.tutorID = tutor
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash("Error entering request to database: " + str(e))
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
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(userEmail=username).first()
        
        if user and check_hash(user.userPassword, password):
            login_user(user)
            session['user'] = username
            session['userID'] = user.userID
            return redirect('/home')
        else:
            flash('Invalid username or password')
    return render_template("login.html")      

# @app.route('/login', methods=['GET'])
# def load_login():
#     return render_template("login.html")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Register route
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
# @app.route('/register', methods=['GET'])
# def load_register():
#     return render_template("register.html")

# @app.route('/register', methods=['POST'])
# def do_register():
#     username = request.form['username']
#     password = request.form['password']
#     user = load_user(username)
#     if user:
#         flash("Username already taken")
#         #Create login button for user to move to login
#     elif(username and password):
#         hashed = hash_pass(password)
#         try:
#             with sqlite3.connect("user.db") as con_user:  
#                 cur_user = con_user.cursor()    
#                 cur_user.execute("INSERT INTO user (userEmail,userPassword) VALUES (?,?)",(username,hashed))    
#                 con_user.commit()
#             do_login()                     
#         except:
#             con_user.rollback()
#             flash("Eror entering user to database")
#     else:
#         flash("Enter valid username and password")
#     return redirect('/home')
@app.route('/register', methods=['GET', 'POST'])
def do_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(userEmail=username).first()
        if user:
            flash("Username already taken")
        elif username and password:
            hashed = hash_pass(password)
            try:
                new_user = User(userEmail=username, userPassword=hashed)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                session['user'] = username
                session['userID'] = new_user.userID
                return redirect('/home')
            except Exception as e:
                db.session.rollback()
                flash("Error entering user to database: " + str(e))
        else:
            flash("Enter valid username and password")
    return render_template("register.html")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Logout route
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/home')
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Main
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
if __name__ == "__main__":
    check_databases()
    app.secret_key = os.urandom(12)
    app.run(debug=True,port=4000)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~