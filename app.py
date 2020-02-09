import os
from datetime import timedelta
from functools import wraps

from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_bootstrap import Bootstrap
from werkzeug.urls import url_encode

from utils import databaseUtils




def require_login(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if 'user' not in session:
            flash("Please log in to create posts")
            return redirect(url_for("login"))
        else:
            return f(*args, **kwargs)

    return inner


app = Flask(__name__)
app.secret_key = os.urandom(16)
Bootstrap(app)

@app.template_global()
def modify_query(origin, **new_values):
    args = request.args.copy()

    for key, value in new_values.items():
        args[key] = value

    return '{}?{}'.format(origin, url_encode(args))


@app.route('/')
def root():
    return render_template("home.html")


@app.route("/posts")
def posts():
    return render_template("posts.html", posts=databaseUtils.all_post())


@app.route("/details")
def details():
    post = (databaseUtils.get_post_by_id(request.args.get('postid')))
    postDetails = [post['title'], post['description'], post['loc'], post['skills']]

    return render_template("post.html", post=postDetails)


@app.route("/report")
@require_login
def report():
    return render_template("report.html")


@app.route("/report_button")
def report_button():
    flash("Thank you for your support!")
    return render_template('report.html')



@app.route("/post", methods=["POST"])
@require_login
def post():
    if "title" not in request.form or "description" not in request.form:
        flash("Please fill out title and description")
        return redirect(url_for("createpost"))
    else:
        temp = databaseUtils.create_post(request.form['title'], request.form['description'], request.form['loc'], request.form['skills'],
                                         session['user'])
        flash("Post Created!")
        return redirect(url_for('posts'))


@app.route("/createpost")
@require_login
def createpost():
    return render_template("create.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect(url_for('login'))


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
