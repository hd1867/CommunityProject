from _sha256 import sha256
from bson import ObjectId

import pymongo as pymongo

client = pymongo.MongoClient("mongodb+srv://admin:pass@thecommunityproject-lawyq.gcp.mongodb.net/test?retryWrites=true&w=majority")
db = client.Users
users = db.users
posts = db.posts



def create_user(username, password):
    if get_user_by_name(username) is None:
        user = users.insert_one({
            "username": username,
            "password": hash_password(username, password),
            "postId": []})
        return user.inserted_id
    return None


def get_user_by_name(username):
    return users.find_one({"username": username})


def get_user_by_id(userid):
    return users.find_one({"_id": ObjectId(userid)})


def hash_password(username, password):
    return sha256(str(username+password).encode('utf-8')).hexdigest()


def authenticate(username, password):
    user = get_user_by_name(username)
    if user is None:
        return
    if hash_password(username, password) != user[password]:
        return
    return user["_id"]


def create_post(title, desc, username, skills, _id):
    user = get_user_by_name(username)
    if get_post_by_id(_id) is None:
        post = posts.insert_one({
            "title": title,
            "desc": desc,
            "user": user,
            "skills": skills})
        return post.inserted_id
    return None


def get_post_by_id(post_id):
    return posts.find_one({"_id": ObjectId(post_id)})


def delete_post():
    return
