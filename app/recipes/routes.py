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
    # BUILD THE RECIPE
    try:
        new_recipe = r.get_json()    
        recipe = Recipe(new_recipe)  
        print(recipe)       
        db.session.add(recipe)
    except:
        return({'error': 'recipe data is good but adding failled'}), 500
    # ADD UNKNOWN INGREDIENTS TO DB
    try:
        ingredients = new_recipe['ingredients'] 
        print('ingredients:', ingredients )
        print('ingredients type:', type(ingredients ))
        
        # TODO: rewrite to make a single call for all db_ingr
        new_ingredients = []
        for i, ingr in enumerate(ingredients):
            print(ingr)
            print(f'name_{i}')
            ingr_name = ingr[f'name_{i}'].lower()
            print(ingr_name)
            
            ingr_db = Ingredient.query.filter_by(name=ingr_name).first()
            
            if not ingr_db:
                ingr_db = Ingredient(ingr_name)
                db.session.add(ingr_db)
                new_ingredients.append(ingr_db)
        
        db.session.commit() # commits recipe & any unknown ingredients
    except: 
        return jsonify({'error':'Adding either the recipe or its ingredients failed'}), 400
    # ADD INGREDIENT LIST TO THE RECIPE
    try: #  recipe ingredients (with ID) definitely in the db
        recipe_db = Recipe.query.filter_by(name=recipe.name).first() # ! recipe.name not unique

        for i, ingr in enumerate(ingredients):
            ingr_name = ingr[f'name_{i}'].lower()
            ingr_db = Ingredient.query.filter_by(name=ingr_name).first()
            
            recipeIngredient = RecipeIngredient(recipe_db.id, ingr_db.id, ingr[f'quantity_{i}'], ingr[f'uom_{i}'])
            db.session.add(recipeIngredient)
        print('about to commit')
        db.session.commit()
            
        return jsonify({'success': 'recipe created'}), 201
    except Exception as e:
        print('error:',e)
        return({'error': 'see log for error'}), 500
    
    
@recipes.route('/update/<int:id>', methods=['POST'])
def update_update(id):
    try: 
        id = int(id)
        updates = r.get_json()
        recipe = Recipe.query.get(id)
        if not recipe:
            return jsonify({'error':'recipe not found'}), 400
        recipe.update(updates)
        db.session.add(recipe)
        db.session.commit()
    except:
        return jsonify({'error': 'could not update recipe'}), 400
    return jsonify({'success': recipe.to_dict()}), 200

@recipes.route('/delete/<int:id>', methods=['DELETE'])
def delete_recipe(id):
    try:
        recipe = Recipe.query.get(id)
        db.session.delete(recipe)
        db.session.commit()
    except:    
        return jsonify({'failure': f'recipe not deleted'}), 400
    return jsonify({'success': f'deleted recipe, id:{id}'}), 204