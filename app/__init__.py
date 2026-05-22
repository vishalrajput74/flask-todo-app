
#APP FACTORY SET UP
import os
from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_wtf.csrf import CSRFProtect
from app.extensions import db, csrf,migrate

#Create database object globally
# db = SQLAlchemy()
# csrf = CSRFProtect()

def create_app(): #factory function which is create flask app
    app =Flask(__name__) #for app start(initialize)
    
     # ===============================
    # DATABASE FIX (Render PostgreSQL safe)
    # ===============================
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///todo.db')

    # Render fix: postgres:// → postgresql://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    # # app.config['SECRET_KEY'] = 'your-secret-key' # for security 
    # app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')
    # app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','sqlite:///todo.db') 
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #Tracking off for avoid extra memory use and make peformance fast
    
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    #Database ko app se connect kara
    db.init_app(app)
    csrf.init_app(app)  # initialize extensions
    migrate.init_app(app, db) 
    #Blueprint ko import krke register kara
    from app.routes.auth import auth_bp  #login/signup related routes
    from app.routes.tasks import tasks_bp

    #register blueprint ne call kri auth_bp pass kiya
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    return app
