from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import UploadSet, IMAGES
from app.models import User
from app import image_uploadset
from pathvalidate import sanitize_filename
import urllib

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(),Length(min=2, max=30)])
	password = PasswordField('Password', validators=[DataRequired()])
	#remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),Length(min=2, max=30)])
    password = PasswordField('Password', validators=[DataRequired(),Length(min=2, max=30),
                            EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm Password')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            username.errors.append('Please use a different username, %s is taken.' % username.data)


class ImageForm(FlaskForm):
    image_file = FileField('Image File', validators=[FileRequired(),FileAllowed(image_uploadset, message='File selected was not an image')])
    submit = SubmitField('Upload')
    def validate_image_file(form,field):
        if field.data:
            filename=sanitize_filename(urllib.parse.unquote(field.data.filename)).replace(" ", "_")
            if len(filename) == 0 or len(filename) > 50:
                field.errors.append('File name must be not be empty or greater than 50 characters.')

            field.data.filename = filename

