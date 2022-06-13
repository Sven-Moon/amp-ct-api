from app import app
from flask import jsonify
from app.models import db, Recipe, RecipeBox, RecipeIngredient, User, Ingredient, Day, Schedule, ShoppingList


@app.route('/test', methods=['GET'])
def test():
    print('api test running')
    return jsonify({"test result": "passed"}), 200


# recipe

# schedule

# user

