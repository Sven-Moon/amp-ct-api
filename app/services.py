from datetime import date, timedelta
from functools import wraps
from flask import jsonify, request
from app.models import Day, RecipeBox, Schedule, User
from app.models import Ingredient, RecipeIngredient, db
import numpy as np
import re
from random import choices
from sqlalchemy.exc import SQLAlchemyError

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

def calc_weights(recipe_ids, userRecipes, schedule):
    # recipe_ids = [int] # recipes: [<Recipe>]
    """Creates a weight for each recipe based on 3 things:
    1) time since last made
    2) User entered recipe preference
    3) meat_option (category) preference
    Each makes up 1/3rd of the decision
    Lowest possible value should be no less than 1/5th the highest such that average frequency of a low rated meal is still detectable by the user
    Range [1,5], each category additive"""
    dates_last_made = []
    # dictionary made so an id search isn't needed with every recipe_id
    recipe_obj_dict = {}
    weights = []
    
    for r in userRecipes:        
        recipe_obj_dict[r.recipe_id] = r
        if r.last_made:
            dates_last_made.append(r.last_made)
            
    print(dates_last_made)
    if dates_last_made:
    # split last made dates into quartiles (never made will be 5th)
        quartiles = np.quantile(dates_last_made, [0.25, 0.5,0.75])
                
    for id in recipe_ids:
        # determine category value
        category = recipe_obj_dict[id].category
        category_value = schedule[category+'_freq']
        # determine time since last made value
        time_value = 3
        last_made = recipe_obj_dict[id].last_made
        if last_made == None: time_value = 5
        elif last_made < quartiles[0]:
            time_value = 1
        elif last_made < quartiles[1]:
            time_value = 2
        elif last_made < quartiles[2]:
            time_value = 3
        else:
            time_value = 4
        # determine recipe preference value (not yet given)
        recipe_pref_value = 3
        
        weights.append(category_value+time_value+recipe_pref_value)
    
    return weights
        
def updateMealplan(id):
    today = date.today()
    user_recipes = RecipeBox.query.filter(RecipeBox.user_id==id, 
                               RecipeBox.schedule==True).all()
    print(user_recipes)
    #recipes = [<RecipeBox>]
    unscheduled_breakfast = []
    unscheduled_lunch = []
    unscheduled_dinner = []
    scheduled_recipes_set = set()
    schedule = Schedule.query.filter_by(user_id=id).first() 
    # schedule = <Schedule>    
    
    # REMOVE PAST DAYS & make scheduled recipes set 
    try:
        days = Day.query.filter_by(user_id=id).all() # days: [Day]   
        for day in days:
            if day.date < today:
                db.session.delete(day)
            else:
                if day.breakfast_recipe_id: scheduled_recipes_set.add(day.breakfast_recipe_id)
                if day.lunch_recipe_id: scheduled_recipes_set.add(day.lunch_recipe_id)
                if day.dinner_recipe_id: scheduled_recipes_set.add(day.dinner_recipe_id)
        db.session.commit()
    except:
        return jsonify({'message': 'error parsing scheduled recipes'}), 500
    
    # create list of b/l/d unscheduled
    try:
        print("recipes",user_recipes)
        for user_recipe in user_recipes:
            # recipe: <RecipeBox>
            print(user_recipe.to_dict())
            if user_recipe.recipe_id not in scheduled_recipes_set:
                print('custom_meal_types',user_recipe.custom_meal_types)
                if re.search('[1]',user_recipe.custom_meal_types):
                    unscheduled_breakfast.append(user_recipe.recipe_id)
                if re.search('[2]',user_recipe.custom_meal_types):
                    unscheduled_lunch.append(user_recipe.recipe_id)
                if re.search('[3]',user_recipe.custom_meal_types):
                    unscheduled_dinner.append(user_recipe.recipe_id)


    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        return error
            
    # DETERMINE DAYS NEEDED TO SCHEDULE
    if days:
        max_date_scheduled = max(max([day.date for day in days]) , today)
        days_scheduled = (max_date_scheduled - today).day
        days_to_schedule = schedule.plan_ahead_days - days_scheduled
    else: 
        days_to_schedule = schedule.plan_ahead_days
        max_date_scheduled = date.today() - timedelta(1)
    # SELECT RECIPES FOR DAYS TO SCHEDULE & PACK INTO DAY()
    for i in range(days_to_schedule):
        day_date = max_date_scheduled + timedelta(1 + i)
        # breakfast
        breakfast_recipe_id = choices(
            unscheduled_breakfast, 
            calc_weights(unscheduled_breakfast, user_recipes, schedule), 
            k=1)
        unscheduled_breakfast.remove(breakfast_recipe_id)
        # lunch 
        lunch_recipe_id = choices(
            unscheduled_lunch, 
            calc_weights(unscheduled_lunch, user_recipes, schedule), 
            k=1)
        unscheduled_lunch.remove(lunch_recipe_id)
        # dinner 
        dinner_recipe_id = choices(
            unscheduled_dinner, 
            calc_weights(unscheduled_dinner, user_recipes, schedule), 
            k=1)
        unscheduled_dinner.remove(dinner_recipe_id)
        # pack & add
        day = Day(id, day_date, breakfast_recipe_id, lunch_recipe_id, dinner_recipe_id)    
        db.session.add()
    # commit
    db.session.commit()