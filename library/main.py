import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_mail import Mail
from config import app_config
from azblobexplorer import AzureBlobDelete

config_name = os.getenv('FLASK_ENV', 'default')

app = Flask(__name__)

# change DB Postgres <--> SQLite3
app.config.from_object(app_config['defaultPG'])

db = SQLAlchemy(app)

migrate = Migrate(app, db, render_as_batch=True) # obj for db migrations
CORS(app)

app.config['UPLOAD_FOLDER'] = 'uploads/'

az = AzureBlobDelete(app.config['AZURE_ACCOUNT_NAME'], app.config['AZURE_ACCOUNT_KEY'], app.config['CONTAINER_NAME'])

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Mail configuration
mail = Mail(app)
print(f"Mail server: {app.config['MAIL_SERVER']}, Mail username: {app.config['MAIL_USERNAME']}")


from library.routes import user_routes, role_routes, residents_routes, unit_routes, auth, dev_routes, bill_routes, bill_history_routes, upload_route
