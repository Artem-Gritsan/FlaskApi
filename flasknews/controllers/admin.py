from flask import jsonify, request
from werkzeug.security import generate_password_hash
from db import db
from models.user import User, UserRating
from decorators.check_admin import check_root
from decorators.jwt_decorator import token_required
from constans.http_status_codes import *


@token_required
@check_root
def del_user(current_user, public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message': 'No user found!'}), HTTP_400_BAD_REQUEST
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'The user has been deleted!'}), HTTP_200_OK



@token_required
@check_root
def get_users(current_user):
    users = User.query.all()
    output = []
    for user in users:
        data = {}
        data['public_id'] = user.public_id
        data['name'] = user.name
        data['password'] = user.password
        data['admin'] = user.admin
        data['rating'] = db.session.query(db.func.avg(UserRating.rating)).filter(UserRating.user==user).scalar() or 2.5
        output.append(data)
    return jsonify({'users': output}), HTTP_200_OK


@token_required
@check_root
def get_one_user(current_user, public_id):
    user = User.query.filter_by(public_id=public_id).first() or 0
    if user == 0:
        return jsonify({'message': 'No user found!'}), HTTP_400_BAD_REQUEST
    data = {}
    data['public_id'] = user.public_id
    data['name'] = user.name
    data['password'] = user.password
    data['admin'] = user.admin
    data['rating'] = db.session.query(db.func.avg(UserRating.rating)).filter(UserRating.user == user).scalar() or 2.5
    return jsonify({'user': data}), HTTP_200_OK


@token_required
@check_root
def change_perm(current_user, public_id):
    user = User.query.filter_by(public_id=public_id).first() or 0
    if user == 0:
        return jsonify({'message': 'No user found!'}), HTTP_400_BAD_REQUEST
    user.admin = True
    db.session.commit()
    return jsonify({'message': 'The user has been promoted'}), HTTP_200_OK


@token_required
@check_root
def change_details(current_user, public_id):
    user = User.query.filter_by(public_id=public_id).first() or 0
    if user == 0:
        return jsonify({'message': 'No user found!'}), HTTP_400_BAD_REQUEST
    data = request.get_json()
    user.name = data['name']
    user.password = generate_password_hash(data['password'], method='sha256')
    db.session.flush()
    db.session.commit()
    return jsonify({'message': 'Changed!'}), HTTP_200_OK