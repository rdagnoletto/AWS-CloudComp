from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def get_user(ident):
	return User.query.get(int(ident))


class User(db.Model, UserMixin):
	# add in checks to make sure password or username is not too long
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
    # add in checks to make sure image file is not too long
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_name = db.Column(db.String(80), unique=True, nullable=False)
    num_faces = db.Column(db.Integer, unique=False, nullable=True)

    def __repr__(self):
        return '<Image %r>' % self.id

