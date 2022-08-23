from functools import wraps
from flask import request, jsonify
import jwt, os
from models.user import User
from dotenv import load_dotenv
from constans.http_status_codes import *

load_dotenv()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing!'}), HTTP_401_UNAUTHORIZED
        try:
            data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), HTTP_401_UNAUTHORIZED
        return f(current_user, *args, **kwargs)
    return decorated