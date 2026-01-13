from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from project.main.routes import main
    from project.users.routes import users
    
    app.register_blueprint(main)
    app.register_blueprint(users)

    return app

def create_database(app):
    with app.app_context():
        db.create_all()
        print('Created Database!')
        seed_database(app)

def seed_database(app):
    with app.app_context():
        from project.models import Plan
        if Plan.query.first() is None:
            plan = Plan(name='Monthly', price=999, razorpay_plan_id='CREATE_YOUR_OWN_RAZORPAY_PLAN_ID')
            db.session.add(plan)
            db.session.commit()
            db.session.commit()
            print('Seeded Database!')
