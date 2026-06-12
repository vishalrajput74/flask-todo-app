
#APP FACTORY SET UP
import os
from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_wtf.csrf import CSRFProtect
from app.extensions import db, csrf,migrate,mail
from datetime import timedelta


#Create database object globally
# db = SQLAlchemy()
# csrf = CSRFProtect()

def create_app(): #factory function which is create flask app
    app =Flask(__name__) #for app start(initialize)
    
     # ===============================
    # DATABASE FIX (Render PostgreSQL safe)
    # ===============================
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///todo.db')
    # print("DATABASE URL:", db_url)

    # Render fix: postgres:// → postgresql://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key")
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
    app.config["SESSION_PERMANENT"] = False 
    
      # ── Flask-Mail (local: sirf print karega terminal mein) ──
    app.config["MAIL_SERVER"]         = os.environ.get("MAIL_SERVER", "sandbox.smtp.mailtrap.io")
    app.config["MAIL_PORT"]           = int(os.environ.get("MAIL_PORT", 2525))
    app.config["MAIL_USE_TLS"]        = os.environ.get("MAIL_USE_TLS", "True") == "True"
    app.config["MAIL_USERNAME"]       = os.environ.get("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"]       = os.environ.get("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER")
    app.config["MAIL_USE_SSL"] = os.environ.get("MAIL_USE_SSL", "False") == "True"
    
    
    #Database ko app se connect kara
    db.init_app(app)
    csrf.init_app(app)  # initialize extensions
    migrate.init_app(app, db) 
    mail.init_app(app) 
    #Blueprint ko import krke register kara
    from app.routes.auth import auth_bp  #login/signup related routes
    from app.routes.tasks import tasks_bp

    #register blueprint ne call kri auth_bp pass kiya
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    return app
