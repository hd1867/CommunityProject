from _sha256 import sha256
from bson import ObjectId

import pymongo as pymongo

client = pymongo.MongoClient("mongodb+srv://admin:pass@thecommunityproject-lawyq.gcp.mongodb.net/test?retryWrites=true&w=majority")
db = client.Users
users = db.users


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


def create_post():
    return None


def get_post_by_id(userid):
    return None


def delete_post():
    return None


def all_post_by_user(userid):
    return None


def all_post():
    return None
