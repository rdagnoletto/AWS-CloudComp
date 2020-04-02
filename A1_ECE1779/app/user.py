from flask import render_template,redirect,url_for,request,g,flash
from flask_login import current_user, login_user, logout_user, login_required


from app import webapp, db
from app.models import User
from app.forms import LoginForm, RegistrationForm
from config import Config



@webapp.route('/',methods=['POST'])
def user_login():
    if current_user.is_authenticated:
        return redirect(url_for('images_view'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            flash('Invalid username or password')
            form.username.errors.append("Username not registered")
            return render_template("main.html", title="Welcome", form=form)
        if not user.check_password(form.password.data):
            form.password.errors.append("Invalid username and password combination")
            return render_template("main.html", title="Welcome", form=form)
        login_user(user)
        return redirect(url_for('images_view'))
    return render_template("main.html", title="Welcome", form=form)


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


@webapp.route('/logout',methods=['GET'])
@login_required
def user_logout():
    logout_user()
    return redirect(url_for('main'))


########################### TA ACCESS #######################


@webapp.route('/api/register', methods=['POST','GET'])
def ta_register():

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')


        if username == None or password == None:
            error_msg = "Welcome"
            return render_template('users/ta_register.html',error_msg=error_msg)


        if username == "" or password == "":
            error_msg = "Error: All fields are required!"
            return render_template('users/ta_register.html',error_msg=error_msg)

        else:


            user = User.query.filter_by(username=username).first()

            print("user query ", user)


            if user is None:
                user = User(username=username)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                #flash('You are now registered')
                error_msg = "Registration Success"
                return render_template('users/ta_register.html',error_msg=error_msg)

            else:
                error_msg = "Duplicate Username!!"
                return render_template('users/ta_register.html',error_msg=error_msg)


    return render_template('users/ta_register.html')


