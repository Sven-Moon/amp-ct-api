from flask import jsonify, Blueprint, request as r
from app.models import Ingredient, RecipeIngredient, db, Recipe

recipes= Blueprint('recipes',__name__, url_prefix='/api/v1/recipes')

@recipes.route('/test', methods=['GET'])
def test():
    print('api test running')
    try:
        recipes = Recipe.query.all()
        print (recipes)
    except:
        return jsonify({'error': 'an unknown error occurred'})
        
    return jsonify({"recipes": [r.to_dict() for r in recipes ]}), 200


@recipes.route('/all', methods=['GET'])
def get_recipes():
    try:
        recipes = Recipe.query.all()
        print (recipes)
    except:
        return jsonify({'error': 'an unknown error occurred'})
        
    return jsonify({"recipes": [r.to_dict() for r in recipes ]}), 200

@recipes.route('/create', methods=['POST'])
def create_recipe():
    print('prior to make recipe try')
    try:
        new_recipe = r.get_json()      
        recipe = Recipe(new_recipe)
        db.session.commit()
    except:
        return({'error': 'recipe recorded but ingredients not saved'})
    try:
        ingredients = new_recipe['ingredients'] 
        
        new_ingredients = False
        for i, ingr in enumerate(ingredients):
            ingr_name = ingr['name'].lower()
            
            ingr_db = Ingredient.query.filter_by(name=ingr_name).first()
            
            if not ingr_db:
                new_ingredients = []
                ingr_db = Ingredient(ingr_name)
                db.session.add(ingr_db)
                new_ingredients.append(ingr_db)
        if new_ingredients:
            db.session.commit()
            
        recipe_db = Recipe.query.filter_by(name=recipe.name).first()   

        for ingr in ingredients:
            ingr_name = ingr['name'].lower()
            ingr_db = Ingredient.query.filter_by(name=ingr_name).first()
            
            recipeIngredient = RecipeIngredient(recipe_db.id, ingr_db.id, ingr['quantity'], ingr['uom'])
            db.session.add(recipeIngredient)
        db.session.commit()
            
        return jsonify({'success': 'recipe created'}), 201
    except Exception as e:
        print(e)
        return({'error': 'see log for error'}), 400
    
    
@recipes.route('/update/<int:id>', methods=['POST'])
def update_update(id):
    try: 
        id = int(id)
        updates = r.get_json()
        recipe = Recipe.query.get(id)
        recipe.update(updates)
        print(recipe.to_dict())
        db.session.add(recipe)
        db.session.commit()
    except:
        return jsonify({'error': 'could not update recipe'}), 400
    return jsonify({'success': recipe.to_dict()}), 200
@recipes.route('/delete/<int:id>', methods=['DELETE'])
def delete_recipe(id):
    try:
        r = Recipe.query.get(id)
        db.session.delete(r)
        db.session.commit()
    except:    
        return jsonify({'failure': f'recipe not deleted'}), 400
    return jsonify({'success': f'deleted recipe, id:{id}'}), 204