from project import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    is_subscribed = db.Column(db.Boolean, default=False)
    subscription = db.relationship('Subscription', backref='user', uselist=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    filename = db.Column(db.String(100), nullable=False)
    thumbnail = db.Column(db.String(100), nullable=False, default='default.jpg')
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Video('{self.title}')"

class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=False)  # in cents
    razorpay_plan_id = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f"Plan('{self.name}', '{self.price}')"

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    razorpay_subscription_id = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f"Subscription('{self.user_id}', '{self.plan_id}')"
