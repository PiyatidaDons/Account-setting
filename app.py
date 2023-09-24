from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import base64
# from flask_session import Session
import pymysql
import hashlib
import binascii
import json
from functools import wraps
salt = "cpe341"

app = Flask(__name__)
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    db='stock_1'
)

cur = conn.cursor()
app.secret_key = "super secret key"

@app.route("/login", methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        dataBase_password = password + salt
        hashed = hashlib.md5(dataBase_password.encode())

        cur.execute("SELECT * FROM user_list WHERE Username = %s AND Password = %s",
                    (username, password))
        record = cur.fetchone()
        if record:
            session['loggedin'] = True
            session['username'] = record[1]
            return redirect(url_for('staff'))
        else:
            msg = "Incorrect"

        conn.commit()
    return render_template('login.html', msg=msg)

def islogin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session or not session['loggedin']:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


def check_manager():
    cur.execute("SELECT Position FROM Staff_List WHERE Staff_Username = %s ",
                (session['username'],))
    check_manager = cur.fetchone()
    return check_manager[0]


@app.route("/staff")
@islogin
def staff():
    return redirect(url_for('home_page'))


@app.route("/")
def home():
    conn.ping(reconnect=True)
    return redirect(url_for('staff'))

@app.route("/staff/home")
@islogin
def home_page():
    return render_template('homepage.html', username=session['username'])

@app.route("/logout")
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route("/staff/profile")
@islogin
def profile():
    cur.execute("SELECT * FROM user_list WHERE Username = %s", (session['username']))
    rows = cur.fetchall()
    return render_template('profiles.html', data = rows)

@app.route("/staff/edit-profile")
@islogin
def editprofile():
    cur.execute("SELECT * FROM user_list WHERE Username = %s", (session['username']))
    rows = cur.fetchall()
    return render_template('profileedit.html', data = rows)

@app.route("/staff/update-profile", methods=['POST'])
@islogin
def updateprofile():
    if request.method == "POST":
        first_name = request.form['first_name']
        surname = request.form['surname']
        email = request.form['email']

        sql = "UPDATE user_list SET Firstname = %s, Surname = %s, Description = %s WHERE Username = %s"
        cur.execute(sql, (first_name, surname, email, session['username']))

        conn.commit()

        return redirect(url_for('profile'))


if __name__ == "__main__":
    app.run(debug=True)