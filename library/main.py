import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy, BaseQuery
from flask_migrate import Migrate
from flask_cors import CORS
from config import app_config

config_name = os.getenv('FLASK_ENV', 'default')

app = Flask(__name__)

# change DB Postgres <--> SQLite3
app.config.from_object(app_config['defaultPG'])

db = SQLAlchemy(app)

migrate = Migrate(app, db, render_as_batch=True) # obj for db migrations
CORS(app)


from library.routes import user_routes, role_routes, residents_routes, unit_routes, auth, dev_routes