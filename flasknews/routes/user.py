from flask import Blueprint
from controllers import user


users = Blueprint('user', __name__)


@users.post('/api/v1/user/register')
def create_user():
    return user.create_user()


@users.post('/api/v1/user/login')
def login():
    return user.login()

@users.get('/api/v1/user/me')
def get_my_data():
    return user.get_my_data()


@users.delete('/api/v1/user/me')
def del_my_data():
    return user.get_my_data()


@users.patch('/api/v1/user/me')
def change_my_data():
    return user.change_my_data()


@users.post("/api/v1/post/<post_id>/rating")
def add_post_rating(post_id):
    return user.add_post_rating(post_id)


@users.post("/api/v1/user/<public_id>/rating")
def add_user_rating(public_id):
    return user.add_user_rating(public_id)