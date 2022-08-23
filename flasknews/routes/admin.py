from flask import Blueprint
from decorators.jwt_decorator import token_required
from controllers import admin

admins = Blueprint('admin', __name__)

@admins.delete('/api/v1/user/<public_id>')
@token_required
def del_user(current_user, public_id):
    return admin.del_user(current_user, public_id)


@admins.get('/api/v1/users')
@token_required
def get_users(current_user):
    return admin.get_users(current_user)

@admins.get('/api/v1/user/<public_id>')
@token_required
def get_one_user(current_user, public_id):
    return admin.get_one_user(current_user, public_id)


@admins.patch('/api/v1/user/<public_id>/permission')
@token_required
def change_perm(current_user, public_id):
    return admin.change_perm(current_user, public_id)


@admins.patch('/api/v1/user/<public_id>')
@token_required
def change_details(current_user, public_id):
    return admin.change_details(current_user,public_id)


