from flask import jsonify, Blueprint, request as r
from app.models import db, User
from ..services import token_required


user= Blueprint('user',__name__, url_prefix='/api/v1/user')

@user.route('/test', methods=['GET'])
def test():
    print('api test running')
    return jsonify({"test result": "passed"}), 200

@user.route('/get_all', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify({"users": [user.to_dict() for user in users]})

@user.route('/register', methods=['POST'])
def create_user():    
    try:    
        data = r.get_json()
        username = User.query.filter_by(username=data['username']).first()
        email = User.query.filter_by(email=data['email']).first()
        if username:
            return ('That username is already in use')
        if email:
            return ('That email is already in use')
        else:
            try:
                new_user = User(data['email'], data['username'])
            except:
                return jsonify({'error': 'improper request or body data'}), 400            
    except:
        print('didn\'t get data')    
    
    try:
        db.session.add(new_user)
        db.session.commit()
    except:
        return jsonify({'error':'Server error. User not added.'})
    
    return jsonify({'Success': 'User created'}), 201
