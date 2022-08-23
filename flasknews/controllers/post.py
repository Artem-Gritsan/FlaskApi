from flask import jsonify, request
from db import db
from models.post import Post, PostRating, Comment
from decorators.jwt_decorator import token_required
from decorators.check_admin import check_root
from constans.http_status_codes import *



@token_required
@check_root
def create_post(current_user):
    data = request.get_json()
    if data:
        post = Post(title=data['title'], content=data['content'])
    else:
        return jsonify({'message': 'No data found!'}), HTTP_400_BAD_REQUEST
    db.session.add(post)
    db.session.commit()
    return jsonify({'message': 'Post has been created'}), HTTP_201_CREATED



def get_post(post_id):
    post = Post.query.filter_by(id=post_id).first()
    avg_rating = db.session.query(db.func.avg(PostRating.rating)).filter(PostRating.post_id==post_id).scalar() or 0
    data = {}
    data['title'] = post.title
    data['text'] = post.content
    data['rating'] = avg_rating
    if data:
        return jsonify({'post': data}), HTTP_200_OK
    return jsonify({'message': 'No post found!'}), HTTP_400_BAD_REQUEST


@token_required
def add_comment(current_user, post_id):
    post = Post.query.filter_by(id=post_id).first()
    data = request.get_json()
    if 'parent_id' in data:
        parent = Comment.query.filter_by(id=data['parent_id']).first()
        parent.child = True
        comment = Comment(text=data['message'], post=post, author=current_user, parent=parent)
    else:
        comment = Comment(text=data['message'], post=post, author=current_user)
    comment.save()
    return jsonify({'id': f'{comment.id}'}), HTTP_201_CREATED



def get_comment(post_id):
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.id).all()
    output = []
    count = []
    def recursion(comments, output, post_id, count):
        for comment in comments:
            if comment.id in count:
                pass
            else:
                count.append(comment.id)
                data = {}
                data['id'] = comment.id
                data['author'] = comment.author.name
                data['message'] = comment.text
                data['parent'] = comment.parent_id if comment.parent_id else 'none'
                data['has_child'] = comment.child
                if comment.child is True:
                    output_reply = []
                    comments_reply = Comment.query.filter_by(post_id=post_id, parent=comment).order_by(Comment.id).all()
                    data['reply'] = recursion(comments_reply, output_reply, post_id, count)
                output.append(data)
        return output
    return jsonify({'comments': recursion(comments, output, post_id, count)}), HTTP_200_OK