from flask import Flask
from flask import Flask, flash, redirect, render_template, request, session, abort
import os

app = Flask(__name__)

@app.route('/')
def sendhome():
    return redirect("/home")

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'ASDF' and request.form['username'] == 'admin':
        session['logged_in'] = True
        return redirect("/home")
    else:
        flash('wrong password!')
    return load_login()

@app.route('/login', methods=['GET'])
def load_login():
    return render_template("login.html")

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=4000)