import requests
import os

from flask import Blueprint,render_template,redirect,request,url_for,flash,session,jsonify
# from app import db
from app.extensions import db
from app.models import User
from app.forms import LoginForm, RegisterForm, ChangePasswordForm,ProfileForm,ForgotPasswordForm, ResetPasswordForm
from app.extensions import db, mail
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from flask import current_app
from app.utils import login_required

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
            # print("DEBUG: logged-in user_id=", user.id)
            session['username'] = user.username
            # print("SESSION:", dict(session)) 
            # print("login success")
            # print(" Session after login:", dict(session))
            
            if form.remember_me.data:
                session.permanent = True
            else:
                session.permanent = False
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
            password=hashed_password,
            email=form.email.data

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
@login_required 
def change_password():
    # if 'user_id' not in session:
    #     flash('Please login first', 'error')
    #     return redirect(url_for('auth.login'))

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

@auth_bp.route('/profile', methods=["GET", "POST"])
@login_required
def profile():
    user = db.session.get(User, session['user_id'])
    form = ProfileForm(current_user_id=user.id)

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        db.session.commit()

        # Session update karo — navbar mein naya naam dikhega
        session['username'] = user.username

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))

    elif request.method == "GET":
        # Form mein existing data pre-fill karo
        form.username.data = user.username
        form.email.data = user.email

    return render_template('profile.html', form=form, user=user)

# @auth_bp.route('/forgot-password', methods=["GET", "POST"])
# def forgot_password():
#     # print(" forgot_password route hit") 
#     form = ForgotPasswordForm()

#     if form.validate_on_submit():
#         print("validate form",form.email.data)

#         user = User.query.filter_by(email=form.email.data).first()
#         print(f"DEBUG: User found = {user}")            

#  # TODO: rate limiting add karna hai — last_reset_request field + 2min check

#         if user:
#             print(" User email in DB ", user.email)       
#             print(f"DEBUG: User username = {user.username}")    

#             # Token banao
#             s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
#             token = s.dumps(user.email, salt='password-reset')
#             # print(f"DEBUG: Token generated = {token[:20]}...")

#             # Reset link banao
#             reset_url = url_for('auth.reset_password', token=token, _external=True)
#             # print(f"DEBUG: Reset URL = {reset_url}") 
            
            
#             # Terminal mein print karo (local testing)
#             print("\n" + "="*60)
#             print("PASSWORD RESET LINK (local testing):")
#             print(reset_url)
#             print("="*60 + "\n")

#             # Email bhi bhejo (agar mail configured hai)
#             try:
#                 msg = Message(
#                     subject="Password Reset Request",
#                     recipients=[user.email]
#                 )
#                 msg.body = f"Reset your password using this link:\n\n{reset_url}\n\nLink expires in 10 minutes."
#                 mail.send(msg)
#                 print("Email sent successfully!")
#             except Exception as e:
#                 print(f"Email send failed (use terminal link): {e}")

#         # Security: email exist kare ya na kare, same message dikhao
#         flash('If that email exists, a reset link has been sent.', 'info')
#         # print("DEBUG: Redirecting to login") 
#         return redirect(url_for('auth.login'))
    
#     # print(f"DEBUG: Form errors = {form.errors}")                  
#     return render_template('forgot_password.html', form=form)
@auth_bp.route('/forgot-password', methods=["GET", "POST"])
def forgot_password():
    # print(" forgot_password route hit") 
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        print("validate form", form.email.data)

        user = User.query.filter_by(email=form.email.data).first()
        print(f"DEBUG: User found = {user}")

        # TODO: rate limiting add karna hai — last_reset_request field + 2min check

        if user:
            print(" User email in DB ", user.email)
            print(f"DEBUG: User username = {user.username}")

            # Token banao
            s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = s.dumps(user.email, salt='password-reset')
            # print(f"DEBUG: Token generated = {token[:20]}...")

            # Reset link banao
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            # print(f"DEBUG: Reset URL = {reset_url}")

            # Terminal mein print karo (local testing)
            print("\n" + "="*60)
            print("PASSWORD RESET LINK (local testing):")
            print(reset_url)
            print("="*60 + "\n")

            # Email bhejo
            try:
                sg_key = current_app.config.get('SENDGRID_API_KEY')

                if sg_key:
                    # Render pe → SendGrid HTTP API (port 443)
                    response = requests.post(
                        "https://api.sendgrid.com/v3/mail/send",
                        headers={
                            "Authorization": f"Bearer {sg_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "personalizations": [{"to": [{"email": user.email}]}],
                            "from": {"email": current_app.config['MAIL_DEFAULT_SENDER']},
                            "subject": "Password Reset Request",
                            "content": [{
                                "type": "text/plain",
                                "value": f"Reset your password:\n\n{reset_url}\n\nLink expires in 10 minutes."
                            }]
                        }
                    )
                    print(f"SendGrid HTTP API response: {response.status_code}")

                else:
                    # Local pe → Flask-Mail (Gmail SMTP)
                    msg = Message(
                        subject="Password Reset Request",
                        recipients=[user.email]
                    )
                    msg.body = f"Reset your password using this link:\n\n{reset_url}\n\nLink expires in 10 minutes."
                    mail.send(msg)
                    print("Email sent via Flask-Mail!")

            except Exception as e:
                print(f"Email send failed (use terminal link): {e}")

        # Security: email exist kare ya na kare, same message dikhao
        flash('If that email exists, a reset link has been sent.', 'info')
        # print("DEBUG: Redirecting to login")
        return redirect(url_for('auth.login'))

    # print(f"DEBUG: Form errors = {form.errors}")
    return render_template('forgot_password.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=["GET", "POST"])
def reset_password(token):
    # print("reset route hit")
    # print("token recieved",token)
    # Token verify karo
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='password-reset', max_age=600)# 10 min
        # print("decode emial",email)
    except SignatureExpired: #5 second time duration test
        print("token expired")
        flash('Reset link has expired. Please request a new one.', 'error')
        return redirect(url_for('auth.forgot_password'))
    except BadSignature: #token change reset link like hello world garbage token 
        print("token invalid")
        flash('Invalid reset link.', 'error')
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        # print("form validate")
        # print("user email",email)
        user = User.query.filter_by(email=email).first()
        # print("user found ",user)
        if user:
            print("old hash",user.password)

            user.password = generate_password_hash(form.password.data)
            db.session.commit()
            print("new hash",user.password)
            print("store in db")

            flash('Password reset successful! Please login.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('reset_password.html', form=form)




