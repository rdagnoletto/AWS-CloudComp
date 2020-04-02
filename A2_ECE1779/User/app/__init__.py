import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_uploads import UploadSet, IMAGES, configure_uploads

from config import Config

# initializing the webapp, config, db, login_manager, and flask_uploads
webapp = Flask(__name__)
webapp.config.from_object(Config)
db = SQLAlchemy(webapp)
login_manager = LoginManager(webapp)
image_uploadset = UploadSet('images', IMAGES)
image_uploadset.extensions = image_uploadset.extensions + ('JPG',)
configure_uploads(webapp, (image_uploadset,))

from app import user
from app import image

# creating directories for images if they don't exist yet
originals_dir = os.path.join(os.getcwd(),'images','originals')
faces_dir = os.path.join(os.getcwd(),'images','faces')

if not os.path.exists(originals_dir):
    os.makedirs(originals_dir)
if not os.path.exists(faces_dir):
    os.makedirs(faces_dir)
