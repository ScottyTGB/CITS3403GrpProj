from flask import Flask, flash, redirect, render_template, request, session, abort
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

import os
env_path = os.path.join('.config', 'config.env')

if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            key, value = line.strip().split('=')
            os.environ[key] = value


app = Flask(__name__)

app.config['SECRET_KEY'] = secret_key = os.environ.get('SECRET_KEY')

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):

    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(username):
    # Replace this with user data access
    users = {
        'admin': User(1, 'admin', 'adasdsadwewarsdagertrtegtrg')
    }
    return users.get(username)

#def hash_pass(password):

@app.route('/profile')
def profile():
    print(session['user'])
    if (session['user']):
        return f"Welcome {session['user']}"
    return f"error"

@app.route('/')
def sendhome():
    return redirect("/home")

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']
    
    user = load_user(username)
    
    if user and user.password == password:
        login_user(user)
        session['user'] = username
        print(session['user'])
        return redirect('/home')
    else:
        return 'Invalid username or password'       

@app.route('/login', methods=['GET'])
def load_login():
    return render_template("login.html")

@app.route('/register', methods=['GET'])
def load_register():
    return render_template("register.html")

@app.route('/register', methods=['POST'])
def do_register():
    #Check if username already taken
    print("implementing")
    #else hash password and save to databasea

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return home()

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=4000)