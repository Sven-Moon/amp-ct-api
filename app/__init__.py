from flask import Flask
from config import Config
from .models import db
from flask_migrate import Migrate
from .user.routes import user
from .recipes.routes import recipes
from .meal_plan.routes import meal_plan
from flask_cors import CORS
import stripe


stripe.api_key = 'sk_test_51LAQTdJvxpEoTgBTUcxBvsb3HLNl7nsVl3r75XEmlzsR3zShyv34m3VtZ2vObJWe9Vkz6kPnwkIknElSssAewlbl00AVuisEhJ'

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app,db)
CORS(app, origins=['http://127.0.0.1:3000/', 'http://localhost:3000','http://localhost:3000/', 'http://localhost:3000/register', 'https://auto-meal-planner-ct.web.app/*', 'https://auto-meal-planner-ct--amp-ct-try*-*.web.app'],)

app.register_blueprint(user)
app.register_blueprint(recipes)
app.register_blueprint(meal_plan)


from . import routes
