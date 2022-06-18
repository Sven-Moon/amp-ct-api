import requests as r
from flask import jsonify, Blueprint
from app.models import db, User, Schedule

schedule= Blueprint('schedule',__name__, url_prefix='/api/v1/schedule')

@schedule.route('/test', methods=['GET'])
def test():
    print('api test running')
    return jsonify({"test result": "passed"}), 200

@schedule.route('/schedule/<string:id>/create', methods=['POST'])
def create_schedule(id):
    user = User.query.get(id)
    print(user)
    print(user.username)
    
    
    return jsonify({'schdule created': 'user: '}), 201