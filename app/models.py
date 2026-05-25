# from app import db
from app.extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)

    # relation
    tasks = db.relationship('Task', backref='user', lazy=True)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default="Pending")
    due_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.String(20), nullable=True)
    # foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))