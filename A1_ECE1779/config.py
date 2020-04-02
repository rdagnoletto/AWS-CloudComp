import os

class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
	DB_CONFIG = {'user':'root',
				'password':'Mysql123',
				'host':'127.0.0.1',
				'database':'ece1779_A1'}
	SQLALCHEMY_DATABASE_URI = 'mysql://root:Mysql123@127.0.0.1/ece1779_A1'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	UPLOADED_IMAGES_DEST = "./images/"
