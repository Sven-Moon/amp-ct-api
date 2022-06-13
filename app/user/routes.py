import requests as r
from flask import jsonify, Blueprint
from app.models import db, User
from ..services import token_required


user= Blueprint('user',__name__, url_prefix='/api/v1/user')

@user.route('/test', methods=['GET'])
def test():
    print('api test running')
    return jsonify({"test result": "passed"}), 200

@user.route('/user/register', methods=['POST'])
def create_user(new_user):
    if new_user:
        user = User.query.filter_by(username=new_user.username).first()
    else:
        try:
            new_user = r.get_json()
            user = User(**new_user)
        except:
            return jsonify({'error': 'improper request or body data'}), 400
    try:
        db.session.add(user)
        db.session.commit()
    except:
        return jsonify({'error':'Server error. user not added.'})
    
    return jsonify({'Success': 'User Created'}), 201
