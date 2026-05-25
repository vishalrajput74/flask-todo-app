from datetime import date

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields import DateField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError,Optional,Email
from app.models import User
from wtforms import BooleanField


def validate_future_date(form, field):
    if field.data and field.data < date.today():
        raise ValidationError('Due date cannot be in the past.')
    
    
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=20)
    ])
    email = StringField('Email', validators=[  
        Optional(),
        Email(message='Please enter a valid email')
        ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        # print("Validator running")

        user = User.query.filter_by(username=username.data).first()
        # print("User found:", user)

        if user:
            raise ValidationError('Username already exists!')

class TaskForm(FlaskForm):
    title = StringField('Task', validators=[
        DataRequired(),
        Length(min=3, max=100, message='Task must be between 3 and 100 characters')
    ])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[Optional(),validate_future_date])
    submit = SubmitField('Add Task')

class EditTaskForm(FlaskForm):
    title = StringField('Task Title', validators=[
        DataRequired(),
        Length(min=3, max=100, message='Task must be between 3 and 100 characters')
    ])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Update')
    
class UpdateStatusForm(FlaskForm):
    submit = SubmitField('Update')


class DeleteTaskForm(FlaskForm):
    submit = SubmitField('Delete')

class ClearTasksForm(FlaskForm):
    submit = SubmitField('Clear All Tasks')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')
class BulkActionForm(FlaskForm):
    submit = SubmitField('Apply')