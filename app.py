import base64
import os
from datetime import timedelta
from functools import wraps
from random import randint

from flask import Flask, render_template, request, redirect, flash, url_for, session
from flask_bootstrap import Bootstrap
from werkzeug.urls import url_encode

from utils import databaseUtils


UPLOAD_FOLDER = "static/"



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
    postDetails = [(post)['title'], (post)['description'], (post)['skills'], (post)["_id"], (post)['loc'],
                   (post)['comments'], (post)['picture'], (post)['rsvp']]

    return render_template("post.html", post=postDetails)


@app.route("/report")
@require_login
def report():
    return render_template("report.html")


@app.route("/report_button", methods=["POST"])
def report_button():
    flash("Thank you for your support!")
    temp = databaseUtils.add_report(request.form['report'])
    return redirect('/report')


@app.route("/rsvp_confirm", methods=["GET", "POST"])
@require_login
def rsvp_confirm():
    print("check check check check check check check check check check")
    temp = databaseUtils.rsvp_post(request.args.get("postid"), session['username'])
    flash("You have successfully RSVP'd!")
    return redirect('/posts')


@app.route("/comment", methods=["POST"])
@require_login
def comment():
    dest = "/details" + "?" + "postid=" + request.args.get("postid")
    if "Comment" not in request.form:
        flash("Comments cannot be empty")
        return redirect(dest)
    else:
        print(request.form['Comment'])
        temp = databaseUtils.comment_post(request.args.get("postid"), session['username'], request.form['Comment'])
        return redirect(dest)


@app.route("/post", methods=["GET", "POST"])
@require_login
def post():
    print(request.form)
    if "title" not in request.form or "description" not in request.form:
        flash("Please fill out title and description")
        return redirect(url_for("createpost"))
    else:
        temp = databaseUtils.create_post(request.form['title'], request.form['description'], session['user'],
                                         request.form['loc'], request.form['skills'], session["img_url"], )

        print(temp)
        flash("Post Created!")
        return redirect(url_for('posts'))


@app.route("/createpost", methods=["GET"])
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


@app.route("/imgUP", methods=["POST"])
def imgUP():
    print("Uploading")
    data = request.form["url"]
    encoded_data = data.split(',')[1]
    decoded_data = base64.b64decode(encoded_data)
    filename = "img/" + str(randint(0, 999999999999)) + ".png"
    print(filename)
    filepath = UPLOAD_FOLDER + filename
    f = open(filepath, "wb")
    f.write(decoded_data)
    f.close()
    url = databaseUtils.upload_blob("communityproject-images", filepath, str(randint(0, 999999999999)))
    session['img_url'] = url
    return redirect(url_for("createpost", img_url=url))

@app.route("/auth", methods=["POST"])
def auth():
    if "submit" not in request.form or "user" not in request.form or "pwd" not in request.form:
        flash("At least one form input was incorrect")
        return redirect(url_for('login'))

    if request.form['submit'] == 'Login':
        user = databaseUtils.authenticate(request.form['user'], request.form['pwd'])
        if user:
            session['user'] = str(user)
            session['username'] = databaseUtils.get_user_by_id(user)['username']
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
            session['username'] = databaseUtils.get_user_by_id(success)['username']
            session.permanent = True
            app.permanent_session_lifetime = timedelta(minutes=30)
            return redirect(url_for('root'))
        else:
            flash('This username already exists!')
            return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()
