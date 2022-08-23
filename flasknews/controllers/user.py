from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, jsonify, make_response
from models.user import User, UserRating
from models.post import Post, PostRating
import uuid, jwt, datetime, os
from db import db




def create_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    try:
        new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=True)
        db.session.add(new_user)
        db.session.commit()
    except Exception as ex:
        return jsonify({'message': f'{ex}'})
    return jsonify({'message': 'New user created'})



def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401)
    user = User.query.filter_by(name=auth.username).first()
    if not user:
        return make_response('Could not verify', 401)
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id' : user.public_id,
                            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                            os.getenv('SECRET_KEY'),
                            algorithm="HS256")

        return jsonify({'token': token})
    return make_response('Could not verify', 401)



def get_my_data(current_user):
    user = User.query.filter_by(public_id=current_user.public_id).first()
    data = {}
    data['public_id'] = user.public_id
    data['name'] = user.name
    data['password'] = user.password
    data['admin'] = user.admin
    data['rating'] = db.session.query(db.func.avg(UserRating.rating)).filter(UserRating.user == user).scalar() or 2.5
    return jsonify({f'{user.name}': data})



def del_my_data(current_user):
    user = User.query.filter_by(public_id=current_user.public_id).first()
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Your account has been deleted!'})



def change_my_data(current_user):
    user = User.query.filter_by(public_id=current_user.public_id).first()
    data = request.get_json()
    user.name = data['name']
    user.password = generate_password_hash(data['password'], method='sha256')
    db.session.flush()
    db.session.commit()
    return jsonify({'message': 'Changed!'})



def add_post_rating(current_user, post_id):
    data = request.get_json()
    post = Post.query.filter_by(id=post_id).first()
    rating = PostRating(rating=data['rating'], post=post, user=current_user)
    db.session.add(rating)
    db.session.commit()
    return jsonify({'message': 'Completed'})


def add_user_rating(current_user, public_id):
    data = request.get_json()
    user = User.query.filter_by(public_id=public_id).first()
    rating = UserRating(rating=data['rating'], user=user, from_user=current_user)
    db.session.add(rating)
    db.session.commit()
    return jsonify({'message': 'Completed'})