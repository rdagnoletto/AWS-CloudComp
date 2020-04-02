


from flask import render_template, redirect, url_for, request, flash, Response
from flask_login import current_user, login_user, logout_user, login_required

from app import webapp, db
from app.models_man import User
from app.forms import LoginForm_Manager 


# This handles the user logins, and the homepage is served from here
# If the user is logged in already, they are redirected to the images_view
# This presents a login form on GET requests and processes logins
# on POST requests
@webapp.route('/',methods=['POST', 'GET'])
def user_login():
    if current_user.is_authenticated:
        return redirect(url_for('ec2_list'))

    form = LoginForm_Manager()

    if form.validate_on_submit():

        # If the form is validated, then the provided username and password
        # is checked against the database

        user = User.query.filter_by(username=form.username.data).first()
        print(user)

        if user is None:
            form.username.errors.append("Username not registered")
            return render_template("main.html", title="Welcome", form=form)
        if form.username.data != 'admin':
            form.username.errors.append("You do not have authority to Access this page")
            return render_template("main.html", title="Authorization error ", form=form)

        if not user.check_password(form.password.data):
            form.password.errors.append("Invalid username and password combination")
            return render_template("main.html", title="Welcome", form=form)
        login_user(user)
        return redirect(url_for('ec2_list'))

    return render_template("main.html", title="Welcome", form=form)




# Simple logout function using flask_login when the logout button is clicked
# They are then they are redirected to the login page
@webapp.route('/logout',methods=['GET'])
def user_logout():
    logout_user()
    return redirect(url_for('user_login'))

