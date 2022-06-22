from datetime import datetime, timedelta
from flask import jsonify, Blueprint, request as r
from sqlalchemy import func
from app.models import Ingredient, RecipeBox, RecipeIngredient, db, Recipe, User
from app.services import get_recipe_ingredients
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import SQLAlchemyError


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
    except:
        return jsonify({'error': 'an unknown error occurred'})
        
    return jsonify({"recipes": [r.to_dict() for r in recipes ]}), 200

@recipes.route('/recipebox/<string:username>', methods=['POST'])
def get_user_recipes(username):
    
    try:
        # get user_id: 
        user_id = User.query.filter_by(username=username).first().id
    except:
        return jsonify({'message': 'Error: user not found'}), 401
    # find all the recipe ids in user-recipe
    user_recipes = RecipeBox.query.filter_by(user_id=user_id).all()
    # shape: [UserRecipe_obj] user/recipe ids, scheduling & custom recipe fields    
    # get the recipe data from recipes table
    recipe_ids = [ur.recipe_id for ur in user_recipes] #[int, ...]
    recipe_obj_list = Recipe.query.filter(Recipe.id.in_(recipe_ids)).all()
    # shape: [Recipe_obj]
    # create & fill list of recipes that fills in info from both
    recipes = []
    for i, recipe_obj in enumerate(recipe_obj_list):
        recipe_obj.ingredients = get_recipe_ingredients(recipe_obj.id)
        user_recipe_obj = user_recipes[i] 
        recipe = recipe_obj.to_dict_w_ingredients()
        
        recipe['custom_meal_types'] = user_recipe_obj.custom_instr
        recipe['custom_meat_options'] = user_recipe_obj.custom_meat_options
        recipe['custom_instr'] = user_recipe_obj.custom_instr
        recipe['schedule'] = user_recipe_obj.schedule
        recipe['fixed_schedule'] = user_recipe_obj.fixed_schedule
        recipe['fixed_period'] = user_recipe_obj.fixed_period
        recipe['rating'] = user_recipe_obj.rating
        recipe['cost_rating'] = user_recipe_obj.cost_rating
        recipes.append(recipe)       
    
    return jsonify({'recipes': recipes})

@recipes.route('/<string:username>', methods=['GET'])
def get_recipes_by_user(username):
    print('getting user')
    try:
        user = User.query.filter_by(username=username).first()
        print(user)
        if not user:
            return jsonify('could not find user')
        print('getting recipes')
        print(user['id'])
        recipes = Recipe.query.filter_by(created_by=user['id']).all()
    except:
        return jsonify({'error': 'an unknown error occurred'})
        
    return jsonify({"recipes": [r.to_dict() for r in recipes ]}), 200

@recipes.route('/search', methods=['POST'])
def recipe_search():
    print(r.get_json())
    try:
        filters = r.get_json()
    except:
        return jsonify({'message':'The request looks funny'}), 401
    # never return recipes made by the user (default created_by)
    queries = []
    # only set created_by as a filter if value isn't the username
    if filters['created_by']:
        queries.append(Recipe.created_by==filters['created_by'])
    # normally filter out user, but not if create_by is present
    # user may be looking for their own recipes & they would be filtered
    # out if it wasn't them, anyway
    else:
        queries.append(Recipe.created_by!=filters['username'])
    
    print('hit recipe search')
    print(filters)
    prep_time = filters['prep_time'] if filters['prep_time'] else 999
    cook_time = filters['cook_time'] if filters['cook_time'] else 999
    meat_options = filters['meat_options'] if filters['meat_options'] else ['vegetarian', 'pork', 'fish', 'beef', 'chicken']   
    last_made = filters['last_made'] if filters['last_made'] else 0
    filters['meal_types'] = f'[filters.meal_types]' #regex
    if ['last_made']:
        current_time = datetime.utcnow()
        cutoff = current_time - timedelta(days=last_made)
    else:
        cutoff = datetime.utcnow()
    
    results = Recipe.query.filter(*queries).all()
    # results = Recipe.query.filter(Recipe.created_by==filters['created_by'],
                        #    Recipe.prep_time <= prep_time,
                        #    Recipe.cook_time <= cook_time,
                        #    Recipe.meat_options.in_(meat_options),
                        #    Recipe.meal_types.regex_match(filters.meal_types),
                        #    Recipe.last_made <= cutoff
                        #    )
                        #    Recipe.rating >= filters.rating,
                        #    Recipe.average_cost_rating >= filters.average_cost_rating   
    
    for recipe in results:
        recipe.ingredients = get_recipe_ingredients(recipe.id)
                           
    
    return jsonify({'recipes': [recipe.to_dict_w_ingredients() for recipe in results]}), 200

@recipes.route('/create', methods=['POST'])
def create_recipe():
    # BUILD THE RECIPE
    try:
        new_recipe = r.get_json()    
        recipe = Recipe(new_recipe)
    except:
        return({'message': 'Error: Bad data shape provided'}), 400
    # check for user having same named recipe
    user_recipe_exists = Recipe.query.filter(
        func.lower(Recipe.name)==recipe.name.lower().strip(),
        func.lower(Recipe.created_by)==recipe.created_by.lower()).first()
    if user_recipe_exists:
        return({'message': 'Error: User recipe with this name already exists'}), 400        
    try:    
        db.session.add(recipe)        
    except:
        return({'message': 'Error: Recipe data is good but adding failed'}), 500
    # ADD UNKNOWN INGREDIENTS TO DB
    try:
        ingredients = new_recipe['ingredients'] 
        # TODO: rewrite to make a single call for all db_ingr
        for i, ingr in enumerate(ingredients):
            ingr_name = ingr[f'name_{i}'].lower()
            ingr_db = Ingredient.query.filter_by(name=ingr_name).first()
            if not ingr_db:
                ingr_db = Ingredient(ingr_name)
                db.session.add(ingr_db)
        db.session.commit() # commits recipe & any unknown ingredients
    except: 
        return jsonify({'message':'Error: Commit of either the recipe or its ingredients failed'}), 400
    # ADD INGREDIENT LIST TO THE RECIPE
    try: #  recipe ingredients (with ID) definitely in the db
        recipe_db = Recipe.query.filter_by(name=recipe.name,created_by=recipe.created_by).first()

        for i, ingr in enumerate(ingredients):
            ingr_name = ingr[f'name_{i}'].lower()
            ingr_db = Ingredient.query.filter_by(name=ingr_name).first()
            
            recipeIngredient = RecipeIngredient(
                recipe_db.id, 
                ingr_db.id, 
                ingr[f'quantity_{i}'], ingr[f'uom_{i}'])
            db.session.add(recipeIngredient)
        db.session.commit()
        
        try:
            user_id = User.query.filter_by(username=recipe.created_by).first().id          
            userRecipe = RecipeBox(user_id, recipe.id, recipe.meal_types, recipe.meat_options)
            db.session.add(userRecipe)                       
            db.session.commit()
        except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            print(error)
            return error            
        except:
            return({'message': 'Recipe was created but not added to user Recipe Box. To add it to your box, search for it and add it manually.'}), 207
            
            
        return jsonify({'success': 'Recipe created'}), 201
    except Exception as e:
        print('error:', e)
        return({'message': 'Server error'}), 500
    
@recipes.route('/update/<int:id>', methods=['POST'])
def update_update(id):
    try: 
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

# RECIPEBOX
@recipes.route('/recipebox/<string:username>/add/<int:recipe_id>', methods=['POST'])
def add_recipe_to_recipebox(username,recipe_id):
    
    # get  user id
    print(username)
    print(recipe_id)
    try: 
        opts = r.get_json()
        # username = username.lower()
        print(username)
        user_id = User.query.filter(User.username==username).first().id
        print(user_id)
        recipe = Recipe.query.get(recipe_id)
        if not opts['custom_meal_types']: 
            opts['custom_meal_types'] = str(recipe.meal_types)
        if not opts['custom_meat_options']: 
            opts['custom_meat_options'] = str(recipe.meat_options)
        print(recipe.meat_options)
    except:
        return jsonify({'message': 'Error: User could not be found'}), 400
    # use user_id & recipe_id to create entry
    try:
        user_recipe = RecipeBox(user_id, recipe_id, opts['custom_meal_types'], opts['custom_meat_options'], opts['schedule'], opts['fixed_schedule'], opts['fixed_period'])
    except:
        return jsonify({'message': 'Error: User return bad data'}), 400
    try:
        db.session.add(user_recipe)
        db.session.commit()
    except:
        return jsonify({'message': 'Error: User recipe could not be added'}), 500
            
    return jsonify({'message': 'User recipe added'}), 201

@recipes.route('/recipebox/<string:username>/remove/<int:recipe_id>', methods=['DELETE'])
def remove_recipe_from_recipebox(username,recipe_id):    
    # get  user id
    print(username)
    print(recipe_id)
    try: 
        opts = r.get_json()
        user_id = User.query.filter(User.username==username).first().id
    except:
        return jsonify({'message': 'Error: User could not be found'}), 400
    # use user_id & recipe_id to create entry
    try:
        remove_recipe = RecipeBox.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
    except:
        return jsonify({'message': 'Error: Recipe could not be found in user Recipe box'}), 400
    try:
        db.session.delete(remove_recipe)
        db.session.commit()
    except:
        return jsonify({'message': 'Error: Recipe was found but could not be removed'}), 500
            
    return jsonify({'message': 'User recipe added'}), 201

