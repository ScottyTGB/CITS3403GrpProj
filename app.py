from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from flask_wtf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from initdb import User, Tutor, Request
import os
import sys
#TODO
#Add in remember me cookie
#Flash doesn't work?

#Find and set secret key, start app
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
env_path = os.path.join('.config', 'config.env')

if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            key, value = line.strip().split('=')
            os.environ[key] = value

csrf = CSRFProtect()
app = Flask(__name__)
csrf.init_app(app)
app.config['SECRET_KEY'] = secret_key = os.environ.get('SECRET_KEY')

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

    def get_id(self):
        return self.userID    

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
        print(request.form['unit'])
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

#View my requests route
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route('/myrequests/<searched>', methods=["GET"])
@app.route('/myrequests', methods=["GET"])
@app.route('/myrequests/', methods=["GET"])
@login_required
def view_my_requests(searched = None):
    if request.method == "GET":
        completed_array = []
        open_array = []
        taken_array = []                
        if(searched != None):
            query = db.session.query(Request).filter(Request.unit.like(f'%{searched}%'))
            requests = query.all()
        else:
            requests = Request.query.all()
        for request_info in requests:

            #Requests I have made but not taken
            if(request_info.userID == session['userID'] and request_info.tutorID == None):
                new_request = {"id": request_info.requestID, "unit": request_info.unit}
                open_array.append(new_request)
            
            #Requests I have taken on
            if(request_info.tutorID != None):
                tutor_responded = Tutor.query.get(request_info.tutorID)
                tutor_responded_user = User.query.get(tutor_responded.userID)
                if(tutor_responded_user.userID == session['userID']):
                    user_requesting = User.query.get(request_info.userID)
                    new_request = {"id": request_info.requestID, "user": user_requesting.userEmail, "unit": request_info.unit, "tutor": tutor_responded_user.userEmail}
                    taken_array.append(new_request)

            #Requests I have made and have been taken
            if(request_info.userID == session['userID'] and request_info.tutorID != None):
                tutor_responded = Tutor.query.get(request_info.tutorID)
                tutor_responded_user = User.query.get(tutor_responded.userID)
                user_requesting = User.query.get(request_info.userID)
                new_request = {"id": request_info.requestID, "user": user_requesting.userEmail, "unit": request_info.unit, "tutor": tutor_responded_user.userEmail}
                completed_array.append(new_request)

        return render_template("myrequests.html", completed=completed_array, taken=taken_array, open=open_array)    
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#View completed requests route
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route('/completedrequests/<searched>', methods=["GET"])
@app.route('/completedrequests', methods=["GET"])
@app.route('/completedrequests/', methods=["GET"])
def view_completed_requests(searched = None):
    if request.method == "GET":
        requests_array = []
        if(searched != None):
            query = db.session.query(Request).filter(Request.unit.like(f'%{searched}%'))
            requests = query.all()
        else:
            requests = Request.query.all()
        for request_info in requests:
            if(request_info.tutorID != None):
                user_requesting = User.query.get(request_info.userID)
                tutor_responded = Tutor.query.get(request_info.tutorID)
                tutor_responded_user = User.query.get(tutor_responded.userID)
                new_request = {"id": request_info.requestID, "user": user_requesting.userEmail, "unit": request_info.unit, "tutor": tutor_responded_user.userEmail}
                requests_array.append(new_request)
        return render_template("completedrequests.html", requests=requests_array)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#View Requests route
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route('/requests/<searched>', methods=["GET"])
@app.route('/requests', methods=["GET"]) 
@app.route('/requests/', methods=["GET"])           
def view_requests(searched = None):
    if request.method == "GET":
        requests_array = []
        if(searched != None):
            query = db.session.query(Request).filter(Request.unit.like(f'%{searched}%'))
            requests = query.all()
        else:
            requests = Request.query.all()
        for request_info in requests:
            print(request_info.tutorID)
            if(request_info.tutorID == None):
                print(request_info.userID)
                user_requesting = User.query.get(request_info.userID)
                new_request = {"id": request_info.requestID, "user": user_requesting.userEmail, "unit": request_info.unit}
                requests_array.append(new_request)
        return render_template("requests.html", requests=requests_array)
    
@app.route('/acceptrequest', methods=["POST"])           
@login_required    
def accept_request():
    requestID = request.form.get('selected_id')
    requestPicked = Request.query.get(requestID)
    tutor = session['userID']
    if tutor == requestPicked.userID:
        flash("Cannot accept own request")
    else:
        try:
            new_tutor = Tutor(userID=session['userID'])
            db.session.add(new_tutor)
            db.session.commit()
            requestPicked.tutorID = new_tutor.tutorID
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
        session['username'] = request.form['username']
        
        user = User.query.filter_by(userEmail=username).first()
        
        if user and check_hash(user.userPassword, password):
            login_user(user,remember=True)
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
        session['username'] = request.form['username']
        
        user = User.query.filter_by(userEmail=username).first()
        
        if user:
            flash("Username already taken")
        elif username and password:
            hashed = hash_pass(password)
            try:
                new_user = User(userEmail=username, userPassword=hashed)
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user,remember=True)
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
    session.clear()
    return redirect('/home')
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def print_user_data():
    users = User.query.all()
    for user in users:
        print(f'User ID: {user.userID}, Email: {user.userEmail}, Password: {user.userPassword}')
def print_tutor_data():
    tutors = Tutor.query.all()
    for tutor in tutors:
        print(f'User ID: {tutor.userID}, Tutor ID {tutor.tutorID}')

#Testing route
@app.route("/testing")
def enter_test_data():
    db.session.query(Request).delete()
    db.session.query(Tutor).delete()
    db.session.query(User).delete()

    db.session.commit()
    course_data = ['CITS5501', 'CITS1402', 'CITS5551', 'CITS5552', 'CITS3301', 'CITS4401', 'CITS2402', 'CITS5508', 'CITS3401', 'CITS5504', 'CITS4009', 'CITS4402', 'CITS5553', 'CITS3004', 'CITS1003', 'CITS3006', 'CITS3010']

    test_data = []
    for i in range(15):
        test_data.append(User(userEmail=f"user{i+1}@example.com", userPassword=hash_pass('1')))
        test_data.append(Request(userID=i+1, tutorID=None, unit=course_data[i]))
    db.session.add_all(test_data)
    db.session.commit()

    users = User.query.all()
    for user in users:
        print(f'User ID: {user.userID}, Email: {user.userEmail}, Password: {user.userPassword}')

    for i in range(5):
        new_tutor = Tutor(userID=i+2)
        db.session.add(new_tutor)
        db.session.commit()
        requestPicked = Request.query.get(i+1)
        requestPicked.tutorID = new_tutor.tutorID
        db.session.commit()        

    return redirect("/requests")    

#Sitemap route
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route("/sitemap")
def sitemap():
    return render_template("sitemap.html")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Search route
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@app.route("/searchcomp", methods=['POST'])
@app.route("/searchmy", methods=['POST'])
@app.route("/search", methods=['POST'])
def search_requests():
    search_string = request.form["searched_unit"]
    page = request.url_rule
    print(page)
    if(page.rule == "/searchmy"):
        return redirect(url_for("view_my_requests", searched=search_string))
    elif(page.rule == "/searchcomp"):
        print("hello")
        print(page.rule)
        return redirect(url_for("view_completed_requests", searched=search_string)) 
    else:
        print(page.rule)
        return redirect(url_for("view_requests", searched=search_string))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#Main
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 
if __name__ == "__main__":      
    check_databases()
    app.secret_key = os.urandom(12)
    app.run(debug=True,port=4000)  
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~