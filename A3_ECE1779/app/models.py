from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

from app import webapp

import boto3
from boto3.dynamodb.conditions import Key

#dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url="http://localhost:8000")
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
# tableName = "User"

table = dynamodb.Table(webapp.config['DDB_USER_TBL_NAME'])





##################



class User(UserMixin):

    pass


@login_manager.user_loader
def user_loader(name):
    if table.get_item(Key = {'username' :name}) == None :
        return

    user = User()
    user.id = name
    return user

