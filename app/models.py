from cgi import print_arguments
from datetime import datetime
import secrets
from turtle import back
import uuid
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, SmallInteger, DateTime
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.String(40), primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(40), unique=True, nullable=False)
    
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    token = db.Column(db.String(100))
    
    recipe_owner = db.relationship('Recipe', backref='users')
    shopping_list = db.relationship('ShoppingList', backref='user')
    user_schedule = db.relationship('Schedule', backref='user')
    recipe_box_user = db.relationship('RecipeBox', primaryjoin="User.id==RecipeBox.user_id", backref='user')   
    user_day = db.relationship('Day', backref='user')   
    
    def __init__(self,email,username):
        print(f'In User: {email} - {username}')
        self.id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.token = secrets.token_hex(32)
        print('init complete')
        
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "date_created": self.date_created
        }
        
    def to_dict_reg(self):
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "date_created": self.date_created,
            "access-token": self.token
        }        
        
    def get_token(self):
        return {"access-token": self.token}
    
    def update(self,d):
        for k,v in d.items():
            getattr(self,k)
            setattr(self,k,v)
  
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(75))
    prep_time = db.Column(db.Integer, default=0)
    cook_time = db.Column(db.Integer, default=0)
    instructions = db.Column(db.String(3000))
    category = db.Column(db.String(30))
    meal_types = db.Column(db.String(10))
    image = db.Column(db.String(500))
    rating = db.Column(db.SmallInteger)
    rating_count = db.Column(db.SmallInteger, default=0)
    average_cost_rating = db.Column(db.String(3), default="1")    
    created_by = db.Column(db.String(100), db.ForeignKey('user.username'))
    recipe_box_recipe = db.relationship('RecipeBox', backref='recipes')
    recipe_ingredients = db.relationship('RecipeIngredient', backref='recipe')
    
    def __init__(self, r={}):
        self.name = r.setdefault('name','')
        self.prep_time = r.setdefault('prep_time',0)
        self.cook_time = r.setdefault('cook_time',0)
        self.instructions = r.setdefault('instructions','')
        self.category = r.setdefault('category','')
        self.meal_types = r.setdefault('meal_types',None)
        self.image = r.setdefault('image',None)
        self.rating = r.setdefault('rating',None)
        self.rating_count = r.setdefault('rating_count',0)
        self.average_cost_rating = r.setdefault('average_cost_rating',None)
        self.created_by = r.setdefault('created_by',None)
                        
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "prep_time": self.prep_time,
            "cook_time":self.cook_time,
            "instructions":self.instructions,
            "category":self.category,
            "meal_types":self.meal_types,
            "created_by":self.created_by,
            "image": self.image,
            "rating": self.rating,
            "rating_count": self.rating_count,
            "average_cost_rating": self.average_cost_rating,
            "created_by": self.created_by,
        }
    def to_dict_w_ingredients(self):
        return {
            "id": self.id,
            "name": self.name,
            "prep_time": self.prep_time,
            "cook_time":self.cook_time,
            "instructions":self.instructions,
            "category":self.category,
            "meal_types":self.meal_types,
            "created_by":self.created_by,
            "image": self.image,
            "rating": self.rating,
            "rating_count": self.rating_count,
            "average_cost_rating": self.average_cost_rating,
            "created_by": self.created_by,
            "ingredients": self.ingredients,
            
        }
        
    def update(self,d):
        for k,v in d.items():
            getattr(self,k)
            setattr(self,k,v)

class ShoppingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey("user.id"))
    item_name = db.Column(db.String(50), nullable=False)
    item_qty = db.Column(db.SmallInteger, default=1)
    item_uom = db.Column(db.String(10))
    crossed_off = db.Column(db.Boolean, default=False)
    staple = db.Column(db.Boolean, default=False)
    
    def update(self,d):
        for k,v in d.items():
            getattr(self,k)
            setattr(self,k,v)
    
class Ingredient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(500))
    recipe_ingredient = db.relationship('RecipeIngredient', backref='ingredient')
    
    def __init__(self,name,image="https://res.cloudinary.com/sventerprise/image/upload/v1655141310/CT-amp/qm-food_gbsbwk.png"):
        self.name = name
        self.image = image
    
    def update(self,d):
        for k,v in d.items():
            getattr(self,k)
            setattr(self,k,v)
  
class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey("user.id"))
    # meal frequencies
    veg_freq = db.Column(db.SmallInteger, default=3)
    pork_freq = db.Column(db.SmallInteger, default=3)
    chicken_freq = db.Column(db.SmallInteger, default=3)
    beef_freq = db.Column(db.SmallInteger, default=3)
    fish_freq = db.Column(db.SmallInteger, default=3)  
    # how to mark meal made to reset last_made  
    auto_made = db.Column(db.Boolean, default=True)    
    # how to plan
    store_trip_method = db.Column(db.SmallInteger, default=1)
    store_days_btwn = db.Column(db.SmallInteger, default=7)
    store_trip_days = db.Column(db.SmallInteger, default=6)
        # value format: "1" (Monday), "7" (Sunday), "25"(Tuesday, Friday)
    store_meal_position = db.Column(db.String(10), default="After")
    plan_ahead_days = db.Column(db.SmallInteger, default=14)
    next_store_trip = db.Column(db.DateTime)
    # what to plan
    plan_breakfast = db.Column(db.Boolean, default=True)
    plan_lunch = db.Column(db.Boolean, default=True)
    plan_dinner = db.Column(db.Boolean, default=True)
    
    def __init__(self, schedule) -> None:
        self.user_id: schedule.setDefault('user_id',None)
        self.veg_freq: schedule.setDefault('veg_freq',None)
        self.pork_freq: schedule.setDefault('pork_freq',None)
        self.chicken_freq: schedule.setDefault('chicken_freq',None)
        self.beef_freq: schedule.setDefault('beef_freq',None)
        self.fish_freq: schedule.setDefault('fish_freq',None)
        self.auto_made: schedule.setDefault('auto_made',None)
        self.store_trip_method: schedule.setDefault('store_trip_method',None)
        self.store_days_btwn: schedule.setDefault('store_days_btwn',None)
        self.store_trip_days: schedule.setDefault('store_trip_days',None)
        self.store_meal_position: schedule.setDefault('store_meal_position',None)
        self.plan_ahead_days: schedule.setDefault('plan_ahead_days',None)
        self.next_store_trip: schedule.setDefault('next_store_trip',None)
        self.plan_breakfast: schedule.setDefault('plan_breakfast',None)
        self.plan_lunch: schedule.setDefault('plan_lunch',None)
        self.plan_dinner: schedule.setDefault('plan_dinner',None)
    
    def update(self,d):
        for k,v in d.items():
            getattr(self,k)
            setattr(self,k,v)
    
class Day(db.Model):
    user_id = db.Column(db.String(100), db.ForeignKey('user.id'), primary_key=True)
    date = db.Column(db.DateTime, nullable=False,primary_key=True)
    breakfast_recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))
    lunch_recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))
    dinner_recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))
    
    def __init__(self, user_id,date,breakfast_recipe_id,lunch_recipe_id,dinner_recipe_id):        
        self.user_id = user_id,
        self.date = date,
        self.breakfast_recipe_id = breakfast_recipe_id,
        self.lunch_recipe_id = lunch_recipe_id,
        self.dinner_recipe_id = dinner_recipe_id
    
    
    def update(self,d):
        for k,v in d.items():
            getattr(self,k)
            setattr(self,k,v)
            
            

class RecipeBox(db.Model):
    user_id = db.Column(db.String(100), db.ForeignKey('user.id'), primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), primary_key=True)
    custom_instr = db.Column(db.String(3000), default=None)
    # schedule: whether to consider for schduling
    schedule = db.Column(db.Boolean, default=True, nullable=False)  
    fixed_schedule = db.Column(db.Boolean, default=False, nullable=False)
    fixed_period = db.Column(db.SmallInteger)
    rating = db.Column(db.SmallInteger)
    cost_rating = db.Column(db.SmallInteger)
    last_made = db.Column(db.DateTime)
    
    def __init__(self,user_id, recipe_id, 
                 schedule=True, fixed_schedule=False, fixed_period=14):
        self.user_id = user_id
        self.recipe_id = recipe_id
        self.schedule = schedule
        self.fixed_schedule = fixed_schedule
        self.fixed_period = fixed_period
    
    def update(self,d):
        for k,v in d.items():
            getattr(self,k)
            setattr(self,k,v)
            
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'recipe_id': self.recipe_id,
            'custom_instr': self.custom_instr,
            'schedule': self.schedule,
            'fixed_schedule': self.fixed_schedule,
            'fixed_period': self.fixed_period,   
            'rating': self.rating,
            'cost_rating': self.cost_rating,
            'last_made': self.last_made}

class RecipeIngredient(db.Model):
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), primary_key=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredient.id'), primary_key=True)
    quantity = db.Column(db.String(10), default="1")
    uom = db.Column(db.String(10), default=None)    
    
    def __init__(self,recipe_id,ingredient_id,qty,uom):
        self.recipe_id = recipe_id
        self.ingredient_id = ingredient_id
        self.quantity = qty
        self.uom = uom
    
    def update(self,d):
        for k,v in d.items():
            getattr(self,k)
            setattr(self,k,v)
            
    def to_dict(self):
        return {
            "recipe_id": self.recipe_id ,
            "ingredient_id": self.ingredient_id ,
            "qty": self.quantity ,
            "uom": self.uom 
        }
 