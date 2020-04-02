import urllib

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Email
from flask_wtf.file import FileField, FileRequired, FileAllowed
from pathvalidate import sanitize_filename
from wtforms.fields.html5 import EmailField  

from app.models import User
from app import image_uploadset

import boto3
from boto3.dynamodb.conditions import Key

#dynamodb = boto3.resource('dynamodb', region_name='us-east-1', endpoint_url="http://localhost:8000")
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
tableName = "User"


# These form are defined using flask_wtf in python as opposed to building them in html

class LoginForm(FlaskForm):

    # This is the login form which takes a username and password, and has a submit button
    # This login form is displayed on our main page, and in user.py the form inputs
    # are tested against our registered user data to authenticate and log them in

	username = StringField('Username', validators=[DataRequired(),Length(min=2, max=30)])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):

    # Here is the registration form for new users. Using built in validators we are able to
    # automatically check that the form has been fully filled out with appropriate data

    username = StringField('Username', validators=[DataRequired(),Length(min=2, max=30)])
    password = PasswordField('Password', validators=[DataRequired(),Length(min=2, max=30),
                            EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm Password')
    email = EmailField("Email",  validators=[DataRequired(), Email("Please enter your email address.")])
    submit = SubmitField('Register')


    # A custom validator is also defined for the username to ensure it has not been taken already
    def validate_username(self, username):
        table = dynamodb.Table(tableName)
        response = table.get_item(Key = {'username' : username.data})

        if 'Item' in response:
            username.errors.append('Please use a different username, %s is taken.' % username.data)


        # user = User.query.filter_by(username=username.data).first()
        # if user is not None:
        #     username.errors.append('Please use a different username, %s is taken.' % username.data)


class ImageForm(FlaskForm):

    # This is the form for uploading images. It validates than an image file was given

    image_file = FileField('Image File', validators=[FileRequired(),FileAllowed(image_uploadset, message='File selected was not an image')])
    submit = SubmitField('Upload')

    # This custom validator sanitized the filename and makes sure it is not too long.
    def validate_image_file(form,field):
        if field.data:
            filename=sanitize_filename(urllib.parse.unquote(field.data.filename)).replace(" ", "_")
            if len(filename) == 0 or len(filename) > 50:
                field.errors.append('File name must be not be empty or greater than 50 characters.')

            field.data.filename = filename

class SearchForm(FlaskForm):

    # This is the search form for searching through our pictures

    search_term = StringField('Search', validators=[DataRequired(),Length(max=30)])
    submit = SubmitField('Search Images')

