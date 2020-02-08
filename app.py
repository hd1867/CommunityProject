import os
from datetime import timedelta
from functools import wraps

from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_bootstrap import Bootstrap

from utils import databaseUtils


def require_login(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if 'user' not in session:
            flash("Please log in to view posts")
            return redirect(url_for("login"))
        else:
            return f(*args, **kwargs)
    return inner


app = Flask(__name__)
app.secret_key = os.urandom(16)
Bootstrap(app)


@app.route('/')
def root():
    return render_template("home.html")


@app.route("/posts")
def posts():
    return render_template("posts.html")


@app.route("/report")
@require_login
def report():
    return render_template("report.html")


@app.route("/createpost")
@require_login
def createpost():
    return


@app.route("/about")
def about():
    return render_template("about.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route("/auth", methods=["POST"])
def auth():
    if "submit" not in request.form or "user" not in request.form or "pwd" not in request.form:
        flash("At least one form input was incorrect")
        return redirect(url_for('login'))

    if request.form['submit'] == 'Login':
        user = databaseUtils.authenticate(request.form['user'], request.form['pwd'])
        if user:
            session['user'] = str(user)
            session.permanent = True
            app.permanent_session_lifetime = timedelta(minutes=30)
            return redirect(url_for('root'))
        else:
            flash('Incorrect username or password')
            return redirect(url_for('login'))
    else:
        success = databaseUtils.create_user(request.form['user'], request.form['pwd'])
        if (success):
            session['user'] = str(success)
            session.permanent = True
            app.permanent_session_lifetime = timedelta(minutes=30)
            return redirect(url_for('root'))
        else:
            flash('This username already exists!')
            return redirect(url_for('login'))



if __name__ == '__main__':
    app.run()
