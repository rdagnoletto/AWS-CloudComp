
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_login import LoginManager
from flask_uploads import UploadSet, IMAGES, configure_uploads
import os

webapp = Flask(__name__)
webapp.config.from_object(Config)
db = SQLAlchemy(webapp)
login_manager = LoginManager(webapp)
image_uploadset = UploadSet('images', IMAGES)
configure_uploads(webapp, (image_uploadset,))

from app import main
from app import user
from app import image



directory1 = os.path.join(os.getcwd(),'images','faces')
#directory2 = os.path.join(os.getcwd(),'images','thumbnails')
directory3 = os.path.join(os.getcwd(),'images','originals')

if not os.path.exists(directory1):
    os.makedirs(directory1)
# if not os.path.exists(directory2):
#     os.makedirs(directory2)
if not os.path.exists(directory3):
    os.makedirs(directory3)
