from flask import Flask, jsonify, request, make_response
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://postgres:{os.getenv('PG_PASSWORD')}@localhost/flaskApi"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    admin = db.Column(db.Boolean, default=False)
    comments = db.relationship('Comment', backref='author')

class Post(db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    title = db.Column(db.String(50), unique=True)
    content = db.Column(db.TEXT)
    timestamp = db.Column(db.DateTime(), default=datetime.datetime.utcnow, index=True)
    comments = db.relationship('Comment', backref='post')

class Comment(db.Model):
    _N = 6

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(140))
    author_id = db.Column(db.INTEGER, db.ForeignKey('user.id'))
    post_id = db.Column(db.INTEGER, db.ForeignKey('post.id'))
    timestamp = db.Column(db.DateTime(), default=datetime.datetime.utcnow, index=True)
    path = db.Column(db.Text, index=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    replies = db.relationship(
        'Comment', backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic')

    def save(self):
        db.session.add(self)
        db.session.commit()
        prefix = self.parent.path + '.' if self.parent else ''
        self.path = prefix + '{:0{}d}'.format(self.id, self._N)
        print(self.path)
        db.session.commit()

    def level(self):
        return len(self.path) // self._N - 1


# class Comment(db.Model):
#     pass

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated




@app.post('/api/v1/user/register')
def create_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    try:
        new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
        db.session.add(new_user)
        db.session.commit()
    except Exception as ex:
        return jsonify({'message': f'{ex}'})
    return jsonify({'message': 'New user created'})
@app.delete('/api/v1/user/<public_id>')
def del_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message': 'No user found!'})
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'The user has been deleted!'})

@app.get('/api/v1/users')
@token_required
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
        output.append(data)
    return jsonify({'users': output})

@app.get('/api/v1/user/<public_id>')
@token_required
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
    return jsonify({'user': data})

@app.patch('/api/v1/user/<public_id>/permission')
@token_required
def change_perm(current_user, public_id):
    if not current_user.admin:
        return jsonify({'message': 'Cannot perform this function!'})

    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message': 'No user found!'})
    user.admin = True
    db.session.commit()
    return jsonify({'message': 'The user has been promoted'})

@app.patch('/api/v1/user/<public_id>')
@token_required
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



@app.post('/api/v1/user/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Could not verify', 401)
    user = User.query.filter_by(name=auth.username).first()
    if not user:
        return make_response('Could not verify', 401)
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'public_id' : user.public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, os.getenv('SECRET_KEY'), algorithm="HS256")
        return jsonify({'token': token})
    return make_response('Could not verify', 401)

@app.get('/api/v1/user/me')
@token_required
def get_my_data(current_user):
    user = User.query.filter_by(public_id=current_user.public_id).first()
    data = {}
    data['public_id'] = user.public_id
    data['name'] = user.name
    data['password'] = user.password
    data['admin'] = user.admin
    return jsonify({f'{user.name}': data})

@app.delete('/api/v1/user/me')
@token_required
def del_my_data(current_user):
    user = User.query.filter_by(public_id=current_user.public_id).first()
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Your account has been deleted!'})

@app.patch('/api/v1/user/me')
@token_required
def change_my_data(current_user):
    user = User.query.filter_by(public_id=current_user.public_id).first()
    data = request.get_json()
    user.name = data['name']
    user.password = generate_password_hash(data['password'], method='sha256')
    db.session.flush()
    db.session.commit()
    return jsonify({'message': 'Changed!'})



@app.post('/api/post/add')
def create_post():
    data = request.get_json()
    if data:
        post = Post(title=data['title'], content=data['content'])
    else:
        return jsonify({'message': 'No data found!'})
    db.session.add(post)
    db.session.commit()
    return jsonify({'message': 'Post has been created'})

@app.post('/api/v1/posts/<post_id>/comments')
@token_required
def add_comment(current_user, post_id):
    post = Post.query.filter_by(id=post_id).first()
    data = request.get_json()
    comment = Comment(text=data['message'], post=post, author=current_user)
    comment.save()
    return jsonify({'message': 'Comment has been added'})


@app.get('/api/v1/posts/<post_id>/comments')
def get_comment(post_id):
    data = {}
    comments = Comment.query.filter_by(post_id=post_id).all()
    for comment in comments:
        data['author'] = comment.author.name
        data['message'] = comment.text
        data['path'] = comment.path
        data['lvl'] = len(comment.path) // comment._N - 1
        data['parent'] = comment.parent_id if comment.parent_id else 'none'
        data = [data]

    return jsonify({'comments': data})




if __name__ == '__main__':
    app.run()