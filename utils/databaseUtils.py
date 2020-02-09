from _sha256 import sha256
from bson import ObjectId
from pymongo import MongoClient

import pymongo as pymongo
import base64
import gridfs

client = pymongo.MongoClient("mongodb+srv://admin:pass@thecommunityproject-lawyq.gcp.mongodb.net/test?retryWrites=true&w=majority")
db = client.Users
users = db.users
posts = db.posts
reports = db.reports

db2 = MongoClient().gridfs_eaxmple
fs = gridfs.GridFS(db2)


# creates a user in the database with a username, password, and post id
def create_user(username, password):
    if get_user_by_name(username) is None:
        user = users.insert_one({
            "username": username,
            "password": hash_password(username, password),
            "postId": []})
        return user.inserted_id
    return None


# gets the username of a user
def get_user_by_name(username):
    return users.find_one({"username": username})


# gets the id of a user
def get_user_by_id(userid):
    return users.find_one({"_id": ObjectId(userid)})


# constructs the value for a password key
def hash_password(username, password):
    return sha256(str(username+password).encode('utf-8')).hexdigest()


# provides the information needed for a user to sign in
def authenticate(username, password):
    user = get_user_by_name(username)
    if user is None:
        return
    if hash_password(username, password) != user["password"]:
        return
    return user["_id"]


# creates a post with a title, description, username, skills, and image name
def create_post(title, description, username, loc, skills, pic):
    user = get_user_by_name(username)
    picture = fs.put(pic)
    post = posts.insert_one({
        "title": title,
        "description": description,
        "user": username,
        "loc": loc,
        "picture": picture,
        "skills": skills,
        "comments": []})
    return post.inserted_id


# gets a post by the post id
def get_post_by_id(post_id):
    return posts.find_one({"_id": ObjectId(post_id)})


def comment_post(post_id, user, comment):
    post = (get_post_by_id(post_id))
    if post['comments'] is None:
        post['comments'] = [{"user" : user, "comment" : comment}]
    else:
        post['comments'] += [{"user" : user, "comment" : comment}]
    new_value = {"$set": {"comments": post['comments']}}
    posts.update_one(get_post_by_id(post_id), new_value)


# deletes a post by the post id
def delete_post(post_id):
    posts.delete_one(posts.find_one({"_id": ObjectId(post_id)}))
    return


# returns all of he post between every user
def all_post():
    all_pst = []
    for items in posts.find({}):
        all_pst.append(items)
    return all_pst


# converts an image into type string
def image_to_str(image_name):
    with open(image_name, "rb") as imageFile:
        image_str = base64.b64encode(imageFile.read())
    return image_str


# converts a string into type image
def str_to_image(image_str):
    with open(image_str, "wb") as fimage:
        image = fimage.write(str.decode('base64'))
    return image


# adds a new report to the database
def add_report(report):
    (print(report))
    reports.insert_one({"description": report})


# upgrades a normal user to an admin
def user_admin(userid):
    return None


# returns a picture (image file)
def get_picture(picture):
    return fs.get(picture).read()
