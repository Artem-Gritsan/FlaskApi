from db import db

class User(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    admin = db.Column(db.Boolean, default=False)
    post_rating = db.relationship('PostRating', backref='user')
    rating = db.relationship('UserRating', foreign_keys='UserRating.to_user_id', backref='user')
    from_user_rating = db.relationship('UserRating', foreign_keys='UserRating.from_user_id', backref='from_user')
    comments = db.relationship('Comment', backref='author')


class UserRating(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

