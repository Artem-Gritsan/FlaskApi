from flask import Blueprint
from controllers import post


posts = Blueprint('post', __name__)




@posts.post('/api/post/add')
def create_post():
    return post.create_post()


@posts.get('/api/v1/post/<post_id>')
def get_post(post_id):
    return post.get_post(post_id)


@posts.post('/api/v1/post/<post_id>/comments')
def add_comment(post_id):
    return post.add_comment(post_id)


@posts.get('/api/v1/post/<post_id>/comments')
def get_comment(post_id):
    return post.get_comment(post_id)