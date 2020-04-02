
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


@login_manager.user_loader
def get_user(ident):
	return User.query.get(int(ident))


class User(db.Model, UserMixin):

    # This defines our User model and the db structure using flask_sqlalchemy
    # There is a unique ID, username, and password hash in the user table
    # This builds off a class from flask_login to seemlessly work with
    # authentication and current_user

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Image(db.Model):

    # This is the Image class that defines the image db table
    # It has its own id, the associated user_id as a foreign key,
    # the filename, and the number of faces detected in it.

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_name = db.Column(db.String(80), unique=True, nullable=False)
    num_faces = db.Column(db.Integer, unique=False, nullable=True)

    def __repr__(self):
        return '<Image %r>' % self.id




class AutoScale(db.Model):
    id_scaling = db.Column(db.Numeric,primary_key=True, default=1)
    max_threshold = db.Column(db.DECIMAL(10,2))
    min_threshold = db.Column(db.DECIMAL(10,2))
    add_ratio = db.Column(db.DECIMAL(10,2))
    red_ratio = db.Column(db.DECIMAL(10,2))
    auto_toggle = db.Column(db.BOOLEAN)


