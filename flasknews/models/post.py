from db import db
import datetime


class Post(db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    title = db.Column(db.String(50), unique=True)
    content = db.Column(db.TEXT)
    timestamp = db.Column(db.DateTime(), default=datetime.datetime.utcnow, index=True)
    rating = db.relationship('PostRating', backref=db.backref('post', lazy=True))
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
    child = db.Column(db.Boolean, default=False)
    replies = db.relationship(
        'Comment', backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic')

    def save(self):
        db.session.add(self)
        db.session.flush()
        db.session.commit()
        prefix = self.parent.path + '.' if self.parent else ''
        self.path = prefix + '{:0{}d}'.format(self.id, self._N)
        print(self.path)
        db.session.commit()

    def level(self):
        return len(self.path) // self._N - 1


class PostRating(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)