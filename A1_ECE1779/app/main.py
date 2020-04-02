from flask import render_template,redirect,url_for
from flask_login import current_user

from app import webapp
from app.forms import LoginForm


@webapp.route('/',methods=['GET'])
#Return html with pointers to the examples
def main():
    if current_user.is_authenticated:
        return redirect(url_for('images_view'))
    form = LoginForm()
    return render_template("main.html", title="Welcome!!", form=form)

