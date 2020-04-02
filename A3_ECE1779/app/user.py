from flask import render_template, redirect, url_for, request, flash, Response
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from app import webapp, db #, dynamo
from app.models import User
from app.forms import LoginForm, RegistrationForm

import boto3
from boto3.dynamodb.conditions import Key

#dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url="http://localhost:8000")
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

def create_dynamo_User():

    table = dynamodb.create_table(
        TableName = webapp.config["DDB_USER_TBL_NAME"],
        KeySchema = [
                    {   'AttributeName': 'username',
                        'KeyType': 'HASH'  #Partition key
                    }
                    # ,
                    # {
                    #     'AttributeName': 'password_hash',
                    #     'KeyType': 'RANGE'  #sort key
                    # },
                    ],
        AttributeDefinitions=[ # define columns

                    {
                        'AttributeName': 'username',
                        'AttributeType': 'S'
                    }
                    # ,
                    # {
                    #     'AttributeName': 'password_hash',
                    #     'AttributeType': 'S'
                    # }

                    ],
        ProvisionedThroughput={
                        'ReadCapacityUnits': 2,
                        'WriteCapacityUnits': 2
                    }
        )







# To wait till the db is created .
    client = boto3.client("dynamodb")

    #Wait for the table to exist before exiting
    print('Waiting for User', '...')
    waiter = client.get_waiter('table_exists')
    waiter.wait(TableName=webapp.config["DDB_USER_TBL_NAME"])
    print("Table created")
    return



def putItem_User(username,password,email, images = None ):

    # helper function to add data to table

    table = dynamodb.Table(webapp.config["DDB_USER_TBL_NAME"])
    table_exists = False


    if table.creation_date_time != None:

        print("table exists !! ",table.creation_date_time)
        table_exists = True
    else:
        table_exists = False
        print("table do not exist")
        #print("table:",table)

    if not table_exists:
        create_dynamo()

    response = table.put_item(
       Item={
            'username': username,
            'password_hash': password,
            'email':email,
            'images' : images,
        }
    )

    print("Item addition succeeded")

    return




# This handles the user logins, and the homepage is served from here
# If the user is logged in already, they are redirected to the images_view
# This presents a login form on GET requests and processes logins
# on POST requests
@webapp.route('/login',methods=['POST', 'GET'])
def user_login():
    if current_user.is_authenticated:
        return redirect(url_for('images_view'))

    form = LoginForm()
    if form.validate_on_submit():

        # If the form is validated, then the provided username and password
        # is checked against the database

        user = User()

        ##############

        table = dynamodb.Table(webapp.config["DDB_USER_TBL_NAME"])

        #response = table.scan(IndexName = 'username', KeyConditionExpression= Key('username').eq(form.username.data))
        response = table.get_item(Key = {'username' :form.username.data})

        if 'Item' in response:
            saved_password = response['Item']['password_hash']
            if not check_password_hash(saved_password,form.password.data):
                form.password.errors.append("Invalid username and password combination")
                return render_template("users/login.html", title="Welcome", form=form)
        else:
            form.username.errors.append("Username not registered")
            return render_template("users/login.html", title="Welcome", form=form)

        user.id = form.username.data
        login_user(user)
        return redirect(url_for('images_view'))

    return render_template("users/login.html", title="Welcome", form=form)


# This is for new users using the registration form
# If the form is validated, then the new user is added to the db and logged in
@webapp.route('/user_create',methods=['GET', 'POST'])
def user_create():
    if current_user.is_authenticated:
        return redirect(url_for('images_view'))
    form = RegistrationForm()
    if form.validate_on_submit():

        pswd = generate_password_hash(form.password.data)

        putItem_User(form.username.data,
            pswd,
            email = form.email.data,
            images=[]
             )

        flash('You are now registered')
        user = User()
        user.id = form.username.data
        login_user(user)
        return redirect(url_for('images_view'))
    return render_template('users/new.html', title='New User', form=form)


# Simple logout function using flask_login when the logout button is clicked
# They are then they are redirected to the login page
@webapp.route('/logout',methods=['GET'])
@login_required
def user_logout():
    logout_user()
    return redirect(url_for('home'))



#for creating the User Dynamodb for the first time
@webapp.route('/create_user_db')
def create_user_db():

    create_dynamo_User()


    return "Data added"
