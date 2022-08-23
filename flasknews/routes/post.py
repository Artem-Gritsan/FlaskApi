from flask import Blueprint
from decorators.jwt_decorator import token_required
from controllers import post


posts = Blueprint('post', __name__)




@posts.post('/api/post/add')
@token_required
def create_post(current_user):
    return post.create_post(current_user)


@posts.get('/api/v1/post/<post_id>')
def get_post(post_id):
    return post.get_post(post_id)


@posts.post('/api/v1/post/<post_id>/comments')
@token_required
def add_comment(current_user, post_id):
    return post.add_comment(current_user, post_id)


@posts.get('/api/v1/post/<post_id>/comments')
def get_comment(post_id):
    return post.get_comment(post_id)