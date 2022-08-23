from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, jsonify
from models.user import User, UserRating
from models.post import Post, PostRating
import uuid, jwt, datetime, os
from db import db
from decorators.jwt_decorator import token_required
from constans.http_status_codes import *




def create_user():
    data = request.get_json()
    if len(data['password']) < 6:
        return jsonify({'message': 'Password is too short'}), HTTP_400_BAD_REQUEST
    if len(data['name']) < 4:
        return jsonify({'message': 'Name is too short'}), HTTP_400_BAD_REQUEST
    if data['name'].isalnum() or ' ' in data['name']:
        return jsonify({'message': 'Name should be alphanumeric, also no spaces'}), HTTP_400_BAD_REQUEST
    if User.query.filter_by(name=data['name']).first() is not None:
        return jsonify({'message': 'Name is taken'}), HTTP_409_CONFLICT
    hashed_password = generate_password_hash(data['password'], method='sha256')
    try:
        new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=True)
        db.session.add(new_user)
        db.session.commit()
    except Exception as ex:
        return jsonify({'message': f'{ex}'})
    return jsonify({'message': 'New user created'}), HTTP_201_CREATED



def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({'message':'Could not verify'}), HTTP_401_UNAUTHORIZED
    user = User.query.filter_by(name=auth.username).first()
    if not user:
        return jsonify({'message':'Could not verify'}), HTTP_401_UNAUTHORIZED
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id' : user.public_id,
                            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                            os.getenv('SECRET_KEY'),
                            algorithm="HS256")

        return jsonify({'token': token}), HTTP_200_OK
    return jsonify({'message': 'Could not verify'}), HTTP_401_UNAUTHORIZED


@token_required
def get_my_data(current_user):
    data = {}
    data['public_id'] = current_user.public_id
    data['name'] = current_user.name
    data['password'] = current_user.password
    data['admin'] = current_user.admin
    data['rating'] = db.session.query(db.func.avg(UserRating.rating)).filter(UserRating.user == current_user).scalar() or 2.5
    return jsonify({f'{current_user.name}': data}), HTTP_200_OK


@token_required
def del_my_data(current_user):
    db.session.delete(current_user)
    db.session.commit()
    return jsonify({'message': 'Your account has been deleted!'}), HTTP_200_OK


@token_required
def change_my_data(current_user):
    data = request.get_json()
    current_user.name = data['name']
    current_user.password = generate_password_hash(data['password'], method='sha256')
    db.session.flush()
    db.session.commit()
    return jsonify({'message': 'Changed!'}), HTTP_200_OK


@token_required
def add_post_rating(current_user, post_id):
    data = request.get_json()
    post = Post.query.filter_by(id=post_id).first()
    rating = PostRating(rating=data['rating'], post=post, user=current_user)
    db.session.add(rating)
    db.session.commit()
    return jsonify({'message': 'Completed'}), HTTP_200_OK

@token_required
def add_user_rating(current_user, public_id):
    data = request.get_json()
    user = User.query.filter_by(public_id=public_id).first()
    if UserRating.query.filter_by(rating=data['rating'], user=user, from_user=current_user).first() is not None:
        new_rating = UserRating.query.filter_by(rating=data['rating'], user=user, from_user=current_user).first()
        new_rating.rating = data['rating']
    else:
        rating = UserRating(rating=data['rating'], user=user, from_user=current_user)
        db.session.add(rating)
    db.session.flush()
    db.session.commit()
    return jsonify({'message': 'Completed'}), HTTP_200_OK