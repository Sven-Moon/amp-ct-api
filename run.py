from app import app
from app.models import db, Recipe, RecipeBox, RecipeIngredient, User, Ingredient, Day, Schedule, ShoppingList

@app.shell_context_processor
def shell_context():
    return {
        "db": db,
        "Day": Day,
        "Ingredient": Ingredient,
        "Recipe": Recipe,
        "RecipeBox": RecipeBox,
        "RecipeIngredient": RecipeIngredient,
        "Schedule": Schedule,
        "ShoppingList": ShoppingList,
        "User": User
        }