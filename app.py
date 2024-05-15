from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from initdb import User, Tutor, Request
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

db = SQLAlchemy(app)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Create user, request and login manager
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    userID = db.Column(db.Integer, primary_key=True)
    userEmail = db.Column(db.String(150), unique=True, nullable=False)
    userPassword = db.Column(db.String(150), nullable=False)
    requests = db.relationship('Request', back_populates='user')
    
    def get_id(self):
        return self.userID

class Tutor(db.Model):
    tutorID = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.userID'), nullable=False)
    requests = db.relationship('Request', back_populates='tutor')

class Request(db.Model):
    requestID = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.userID'))
    tutorID = db.Column(db.Integer, db.ForeignKey('tutor.tutorID'))
    unit = db.Column(db.String(150), nullable=False)
    user = db.relationship('User', back_populates='requests')
    tutor = db.relationship('Tutor', back_populates='requests')
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
    
@login_manager.user_loader
def load_user(userID):
    return User.query.get(int(userID))

def check_databases():
    with app.app_context():
        db.create_all()

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
@app.route('/requests', methods=["GET"])           
# @login_required
def view_requests():
    if request.method == "GET":
        requests_array = []
        requests = Request.query.all()
        for request_info in requests:
            if(request_info.tutorID == None):
                user_requesting = User.query.get(request_info.userID)
                new_request = {"id": request_info.requestID, "content": f"{user_requesting.userEmail} has requested tutoring in {request_info.unit}"}
                requests_array.append(new_request)
        return render_template("requests.html", requests=requests_array)
    
@app.route('/acceptrequest', methods=["POST"])           
@login_required    
def accept_request():
    requestID = request.form.get('selected_id')
    print(request.form.get('selected_id'))
    requestPicked = Request.query.get(requestID)
    tutor = session['userID']
    if tutor == requestPicked.userID:
        flash("Cannot accept own request")
    else:
        try:
            requestPicked.tutorID = tutor
            db.session.commit()
            flash("Request accepted successfully")
        except Exception as e:
            db.session.rollback()
            flash("Error entering request to database: " + str(e))
    return redirect('/requests')    
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
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print_user_data() 
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(userEmail=username).first()
        
        if user and check_hash(user.userPassword, password):
            login_user(user)
            session['user'] = username
            session['userID'] = user.userID
            print(f"Login successful for user: {username}") 
            return redirect(url_for('home'))
        else:
            print(f"Login failed for user: {username}") 
            flash('Invalid username or password')
    return render_template("login.html")      
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Register route
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
@app.route('/register', methods=['GET', 'POST'])
def do_register():
    if request.method == 'POST':
        print_user_data() 
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
def print_user_data():
    users = User.query.all()
    for user in users:
        print(f'User ID: {user.userID}, Email: {user.userEmail}, Password: {user.userPassword}')



#Main
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
if __name__ == "__main__":
    check_databases()
    app.secret_key = os.urandom(12)
    app.run(debug=True,port=4000)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~