from functools import wraps
from flask import jsonify, request
from app.models import User

def token_required(api_route):
    @wraps(api_route)
    def decorator_function(*args, kwargs):
        token = request.headers.get('access-token')
        if not token:
            return jsonify({
                'Access Denied': 'No API token, please register to receive your API token'
            }), 401
        if not User.query.filter_by(token=token).first():
            return jsonify({'Access Denied:' 'Invalid API token'}), 403
        
        return api_route(*args,**kwargs)
    return decorator_function