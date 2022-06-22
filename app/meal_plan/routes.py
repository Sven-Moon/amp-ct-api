from datetime import date
from flask import jsonify, Blueprint, request as r
from app.models import Day, RecipeBox, db, User, Schedule
import re
from random import choices

from app.services import calc_weights, updateMealplan

meal_plan= Blueprint('meal_plan',__name__, url_prefix='/api/v1/meal_plan')

@meal_plan.route('/test', methods=['GET'])
def test():
    print('api test running')
    return jsonify({"test result": "passed"}), 200

@meal_plan.route('/<string:id>/schedule/create', methods=['POST'])
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

@meal_plan.route('/<string:id>', methods=['POST'])
def get_meal_plan(id):
    
    updateMealplan(id)
    
    meal_plan = Day.query.filter_by(user_id=id).all()
    
    return jsonify({'meal_plan': meal_plan}), 200