from flask import Flask
import os
from config import Config
from .models import db
from flask_migrate import Migrate
from .user.routes import user
from .recipes.routes import recipes
from .schedule.routes import schedule
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app,db)
CORS(app, origins=['http://127.0.0.1:3000/', 'http://localhost:3000'])

app.register_blueprint(user)
app.register_blueprint(recipes)
app.register_blueprint(schedule)


from . import routes
