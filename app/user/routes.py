from flask import jsonify, Blueprint, request as r
from sqlalchemy import func
from app.models import RecipeBox, db, User
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

@user.route('/reg/<string:email>', methods=['GET'])
def get_registered_user(email):
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify('user not found')
    
    return jsonify({'user': user.to_dict_reg()}),200

@user.route('/get_all', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify({"users": [user.to_dict() for user in users]})

@user.route('/register', methods=['POST'])
def create_user():
    print('hit register')
    try:
        data = r.get_json()
        username = data['username'].strip()
        email = data['email'].lower().strip()
        username_already_present = User.query.filter(
            func.lower(username)==username).first()     
        email_already_present = User.query.filter_by(email=email).first()
    except:
        return ({'message': 'Submitted data type(s) incorrect'}), 400
        
    if username_already_present:
        return ({'message': 'That username is already in use'}), 400
    if email_already_present:
        return ({'message': 'That email is already in use'}), 400
    else:
        try:
            new_user = User(email, username)
        except:
            return jsonify({'message': 'email or username malformed'}), 400    
    try:
        db.session.add(new_user)
        db.session.commit()
    except:
        return jsonify({'message':'Server error. User not added.'}), 500      
    
    return jsonify({'message': 'Success: User created', 'user': new_user.to_dict_reg()}), 200

@user.route('/<string:id>/update', methods=['POST'])
def update_user(id):
    
    # TODO
    
    return jsonify({'message': 'Success: User updated'}), 201

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
    return jsonify({'message': 'Success User deleted'}), 201
