from functools import wraps
from flask import jsonify, request
from app.models import User
from app.models import Ingredient, RecipeIngredient

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

def get_recipe_ingredients(recipe_id):
    # ri = recipe-ingredient
    ri_obj_list = RecipeIngredient.query.filter_by(recipe_id=recipe_id).all()   
    # shape [ <RecipeIngredient>, ... ] 
    
    # shape: [ {recipe_id:v, ingredient_id:v, quantity:v, uom:v}, ... ]
    ingredients = []
    for ri in ri_obj_list:
        ingredient = Ingredient.query.filter_by(id=ri.ingredient_id).first()
        ingredients.append({ 
            'id': ri.ingredient_id,
            'name': ingredient.name,
            'image': ingredient.image,
            'quantity': ri.quantity,
            'uom': ri.uom })
    
    return ingredients
