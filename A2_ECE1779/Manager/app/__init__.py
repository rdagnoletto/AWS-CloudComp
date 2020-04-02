import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_uploads import UploadSet, IMAGES, configure_uploads

from config_man import Config

# initializing the webapp, config, db, login_manager, and flask_uploads
webapp = Flask(__name__)
webapp.config.from_object(Config)
db = SQLAlchemy(webapp)
login_manager = LoginManager(webapp)

from app import main , ec2_examples
