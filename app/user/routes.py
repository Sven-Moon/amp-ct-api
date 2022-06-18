from flask import jsonify, Blueprint, request as r
from app.models import db, User
from ..services import token_required


user= Blueprint('user',__name__, url_prefix='/api/v1/user')

@user.route('/test', methods=['GET'])
def test():
    print('api test running')
    return jsonify({"test result": "passed"}), 200

@user.route('/email/<string:email>', methods=['GET'])
def get_user_by_email(email):
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'user not found'}), 400
    else:    
        return jsonify({'user':user.to_dict()}),200

@user.route('/id/<string:id>', methods=['GET'])
def get_user_by_id(id):
    
    user = User.query.get(id)
    if not user:
        return jsonify('user not found')
    
    return jsonify({'user': user.to_dict()}),200

@user.route('/get_all', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify({"users": [user.to_dict() for user in users]})

@user.route('/register', methods=['POST'])
def create_user():
    print('hit register')
    try:
        data = r.get_json()
        print(data)
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
        print(new_user)
        print('attempting to print new_user.id')
        print(new_user.id)
    except:
        return jsonify({'error':'Server error. User not added.'})        
    
    return jsonify({'msg': 'Success: User created', 'user': new_user}), 200
        

@user.route('/<string:id>/update', methods=['POST'])
def update_user(id):
    
    # TODO
    
    return jsonify({'Success': 'User updated'}), 201

@user.route('/<string:id>/update', methods=['DELETE'])
def delete_user(id):    
    user = User.query.get(id)
    if not user:
        return ('Could not find user')
    else:
        try: 
            User.delete(user)
            db.commit()
        except:
            return jsonify({'error', 'an unknown error occurred'}), 500
    return jsonify({'Success': 'User deleted'}), 201