from flask import render_template, redirect, url_for, request, flash, Response
from flask_login import current_user, login_user, logout_user, login_required

from app import webapp, db
from app.models import User
from app.forms import LoginForm, RegistrationForm


# This handles the user logins, and the homepage is served from here
# If the user is logged in already, they are redirected to the images_view
# This presents a login form on GET requests and processes logins
# on POST requests
@webapp.route('/',methods=['POST', 'GET'])
def user_login():
    if current_user.is_authenticated:
        return redirect(url_for('images_view'))
    form = LoginForm()
    if form.validate_on_submit():

        # If the form is validated, then the provided username and password
        # is checked against the database

        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            form.username.errors.append("Username not registered")
            return render_template("main.html", title="Welcome", form=form)
        if not user.check_password(form.password.data):
            form.password.errors.append("Invalid username and password combination")
            return render_template("main.html", title="Welcome", form=form)
        login_user(user)
        return redirect(url_for('images_view'))
    return render_template("main.html", title="Welcome", form=form)


# This is for new users using the registration form
# If the form is validated, then the new user is added to the db and logged in
@webapp.route('/user_create',methods=['GET', 'POST'])
def user_create():
    if current_user.is_authenticated:
        return redirect(url_for('images_view'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now registered')
        login_user(user)
        return redirect(url_for('images_view'))
    return render_template('users/new.html', title='New User', form=form)


# Simple logout function using flask_login when the logout button is clicked
# They are then they are redirected to the login page
@webapp.route('/logout',methods=['GET'])
@login_required
def user_logout():
    logout_user()
    return redirect(url_for('user_login'))


########################### TA ACCESS #######################


@webapp.route('/api/register', methods=['POST','GET'])
def ta_register():

    # to render the basic html page that will showcase upload api to the world if we get a GET request
    if request.method == 'GET':
        return render_template('users/ta_register.html')


    username = request.form.get('username')
    password = request.form.get('password')

# below are a number of validation checks for the api . These are done using wtforms in the main app

    if username == None or password == None:
        error_msg = "Missing parameters"
        return Response(error_msg, status=401)


    if len(username) <2  or len(username) > 30 or len(password) <2  or len(password) > 30:
        error_msg = "Username or Password do not meet the length requirements"
        return Response(error_msg, status=401)

    else:
        user = User.query.filter_by(username=username).first()

        if user is None:
            try:
                user = User(username=username)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                success_msg = "Registration Success"
                return Response(success_msg, status=201)
            except Exception as error:
                db.session.rollback()
                return Response("DB Error, rollback", status=500)

        else:
            error_msg = "Username is already taken. Please use another one!"
            return Response(error_msg, status=401)


