from flask import Flask, flash, redirect, render_template, request, session, abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
import os

#Find and set secret key
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
env_path = os.path.join('.config', 'config.env')

if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            key, value = line.strip().split('=')
            os.environ[key] = value


app = Flask(__name__)

app.config['SECRET_KEY'] = secret_key = os.environ.get('SECRET_KEY')
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Create user and login manager
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):

    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Helper functions
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def hash_pass(password):
    return generate_password_hash(password)

def check_hash(hash,password):
    return check_password_hash(hash,password)

@login_manager.user_loader
def load_user(username):
    # Replace this with user data access
    users = {
        'admin': User(1, 'admin', 'scrypt:32768:8:1$NoEFfm818doHn0t4$57d676989d1c5d6b02213b255d58b88aeefc040572cbcfdfdee3a318b09c8ff6c0d6aa0514f378ffc25236ef52b689b99acf96e6c3cb12af07b778288a3ebab5')
    }
    return users.get(username)


#Testing user
@app.route('/profile')
def profile():
    print(session['user'])
    if (session['user']):
        return f"Welcome {session['user']}"
    return f"error"
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
        #send username into database
    else:
        flash("Enter valid username and password")
    print("implementing")
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
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=4000)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~