from flask import Blueprint
from controllers import user, post, admin
from decorators.jwt_decorator import token_required


users = Blueprint('user', __name__)


@users.post('/api/v1/user/register')
def create_user():
    return user.create_user()


@users.post('/api/v1/user/login')
def login():
    return user.login()

@users.get('/api/v1/user/me')
@token_required
def get_my_data(current_user):
    return user.get_my_data(current_user)


@users.delete('/api/v1/user/me')
@token_required
def del_my_data(current_user):
    return user.get_my_data(current_user)


@users.patch('/api/v1/user/me')
@token_required
def change_my_data(current_user):
    return user.change_my_data(current_user)


@users.post("/api/v1/post/<post_id>/rating")
@token_required
def add_post_rating(current_user, post_id):
    return user.add_post_rating(current_user, post_id)


@users.post("/api/v1/user/<public_id>/rating")
@token_required
def add_user_rating(current_user, public_id):
    return user.add_user_rating(current_user, public_id)