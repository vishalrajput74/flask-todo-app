from flask import Blueprint,render_template,redirect,request,url_for,flash,session,jsonify
# from app import db
from app.extensions import db
from app.models import User
from app.forms import LoginForm, RegisterForm, ChangePasswordForm
from werkzeug.security import generate_password_hash, check_password_hash

#blueprint object create kara

auth_bp = Blueprint('auth' ,__name__)

@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    # print("Login route Hit")

    form = LoginForm()
    # print(request.method)
    # print("session before ", dict(session))
    
    if form.validate_on_submit():
        # print("form submited")
        # print("username",form.username.data)
        user = User.query.filter_by(username=form.username.data).first()
        # print("user found",user)
        
        # if user and user.password == form.password.data:
        if user and check_password_hash(user.password, form.password.data):

            # session['user'] = user.username
            session['user_id'] = user.id
            session['username'] = user.username
            # print("SESSION:", dict(session)) 

            # print("login success")
            # print(" Session after login:", dict(session))
            flash('Login successful!', 'success')
            return redirect(url_for('tasks.view_tasks'))
        else:
            # print("login failed")
            # print(form.errors)
            flash('Invalid username or password', 'error')
    
    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=["GET", "POST"])
def register():
    # print("Register route hit")
    form = RegisterForm()
   
    
    if form.validate_on_submit():
        # print("form valid")
        # print("username",form.username.data)
        
        hashed_password = generate_password_hash(form.password.data)

        # Create new user
        new_user = User(
            username=form.username.data,
            password=hashed_password

            # password=form.password.data  
        )
        db.session.add(new_user)
        db.session.commit()
        # print("user saved with id",new_user.id)

        # Auto-login
        # session['user'] = new_user.username
        session['user_id'] = new_user.id
        session['username'] = new_user.username 
        # print("session after registration",dict(session))
        
        flash('Registration successful! Welcome!', 'success')
        return redirect(url_for('tasks.view_tasks'))
    # else:
        # print("regsiter failed")
    return render_template('register.html', form=form)

@auth_bp.route('/logout')
def logout():
    # print("before logout session",dict(session))
    session.clear()
    flash('Logged out successfully', 'success')
    # print("after logout session",dict(session))

    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=["GET", "POST"])
def change_password():
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('auth.login'))

    form = ChangePasswordForm()

    if form.validate_on_submit():
        user = db.session.get(User, session['user_id'])

        if not user or not check_password_hash(user.password, form.current_password.data):
            flash('Current password is incorrect!', 'error')
            return redirect(url_for('auth.change_password'))

        user.password = generate_password_hash(form.new_password.data)
        db.session.commit()
        flash('Password changed successfully!', 'success')
        return redirect(url_for('tasks.view_tasks'))

    return render_template('change_password.html', form=form)








