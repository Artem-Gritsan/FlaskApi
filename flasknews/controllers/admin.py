from flask import jsonify, request
from werkzeug.security import generate_password_hash
from db import db
from models.user import User, UserRating



def del_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform this function!'})
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message': 'No user found!'})
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'The user has been deleted!'})



def get_users(current_user):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform this function!'})
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
    return jsonify({'users': output})



def get_one_user(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform this function!'})
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message': 'No user found!'})
    data = {}
    data['public_id'] = user.public_id
    data['name'] = user.name
    data['password'] = user.password
    data['admin'] = user.admin
    data['rating'] = db.session.query(db.func.avg(UserRating.rating)).filter(UserRating.user == user).scalar() or 2.5
    return jsonify({'user': data})



def change_perm(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform this function!'})

    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message': 'No user found!'})
    user.admin = True
    db.session.commit()
    return jsonify({'message': 'The user has been promoted'})


def change_details(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform this function!'})
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message': 'No user found!'})
    data = request.get_json()
    user.name = data['name']
    user.password = generate_password_hash(data['password'], method='sha256')
    db.session.flush()
    db.session.commit()
    return jsonify({'message': 'Changed!'})