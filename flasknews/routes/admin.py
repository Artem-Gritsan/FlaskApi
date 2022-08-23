from flask import Blueprint
from controllers import admin

admins = Blueprint('admin', __name__)

@admins.delete('/api/v1/user/<public_id>')
def del_user(public_id):
    return admin.del_user(public_id)


@admins.get('/api/v1/users')
def get_users():
    return admin.get_users()

@admins.get('/api/v1/user/<public_id>')
def get_one_user(public_id):
    return admin.get_one_user(public_id)


@admins.patch('/api/v1/user/<public_id>/permission')
def change_perm(public_id):
    return admin.change_perm(public_id)


@admins.patch('/api/v1/user/<public_id>')
def change_details(public_id):
    return admin.change_details(public_id)


