from _sha256 import sha256
from bson import ObjectId

import pymongo as pymongo

client = pymongo.MongoClient("mongodb+srv://admin:pass@thecommunityproject-lawyq.gcp.mongodb.net/test?retryWrites=true&w=majority")
db = client.Users
users = db.users
posts = db.posts


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


# creates a post with a title, description, username, and skills field
def create_post(title, desc, username, skills):
    user = get_user_by_name(username)
    post = posts.insert_one({
        "title": title,
        "desc": desc,
        "user": user,
        "skills": skills})
    return post.inserted_id


# gets a post by the post id
def get_post_by_id(post_id):
    return posts.find_one({"_id": ObjectId(post_id)})


# deletes a post by the post id
def delete_post(post_id):
    posts.delete_one(posts.find_one({"_id": ObjectId(post_id)}))
    return


# returns all of he post between every user
def all_post():
    all_pst = []
    for items in posts:
        all_pst.append(items["_id"])
    return all_pst


# upgrades a normal user to an admin
def user_admin(userid):
    return None
