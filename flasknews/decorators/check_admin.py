from functools import wraps
from flask import jsonify

def  check_root(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.admin:
            return f(current_user, *args, **kwargs)
        return jsonify({'message': 'Cannot perform this function!'})
    return decorated