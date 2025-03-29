from flask import Flask
from application.models import db
from application.models import *
import os


app = Flask(__name__,template_folder='../templates',static_folder='../static',instance_relative_config=True)
app.config['secret_key']="abcdefgh"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.secret_key = 'mySecretKey' #protection of sensitive data

BASE_DIR = os.path.abspath(os.path.join(app.root_path, '..'))  # One level up
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#inititate database
db.init_app(app)

#creating tables in project.db
with app.app_context():
    db.create_all()