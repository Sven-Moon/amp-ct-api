from flask import jsonify, Blueprint, request as r
from app.models import db, User, Schedule

schedule= Blueprint('schedule',__name__, url_prefix='/api/v1/schedule')

@schedule.route('/test', methods=['GET'])
def test():
    print('api test running')
    return jsonify({"test result": "passed"}), 200

@schedule.route('/<string:id>/create', methods=['POST'])
def create_schedule(id):
    user = User.query.get(id)
    new_schedule = r.get_json()
    if not user:
        return jsonify({'message': 'error: user not found'}), 400
    
    user_has_schedule = Schedule.query.filter_by(user_id=user.id).first()
    
    if user_has_schedule:
        return ({'message': 'Could not create schedule because one is already associated with this user'}), 400
    
    try:
        sched = Schedule(new_schedule)
        sched.user_id = user.id
    except:
        return jsonify({'message': 'error: unable to create schedule'}), 400
    try:
        db.session.add(sched)
        db.session.commit()
    except:
        return jsonify({'message': 'server error: unable to create schedule'}), 500
    
    return jsonify({'message': 'Schedule created'}), 201

