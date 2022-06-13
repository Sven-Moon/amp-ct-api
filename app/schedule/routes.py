import requests as r
from flask import jsonify, Blueprint
from app.models import db

schedule= Blueprint('schedule',__name__, url_prefix='/api/v1/schedule')

@schedule.route('/test', methods=['GET'])
def test():
    print('api test running')
    return jsonify({"test result": "passed"}), 200


# recipe

# schedule

# user

