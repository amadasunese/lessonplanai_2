from datetime import datetime

from flask_login import UserMixin

from src import bcrypt, db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_confirmed = db.Column(db.Boolean, nullable=True, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

    # Add the relationship to Subscription
    subscription = db.relationship('Subscription', backref='user', uselist=False)

    def __init__(self, email, first_name, last_name, password, 
                 is_admin=False, is_confirmed=False, confirmed_on=None):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password = bcrypt.generate_password_hash(password)
        self.created_on = datetime.now()
        self.is_admin = is_admin
        self.is_confirmed = is_confirmed
        self.confirmed_on = confirmed_on

    def __repr__(self):
        return f"<User {self.email}>" 


class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    plan = db.Column(db.String(50))
    amount = db.Column(db.Integer)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    remaining_usages = db.Column(db.Integer)
    paid = db.Column(db.Boolean, default=False)  # Added paid attribute
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    paystack_subscription_id = db.Column(db.String(50), nullable=False)

    def __init__(self, plan, amount, start_date, end_date, remaining_usages, paid, paystack_subscription_id, user_id):
        self.plan = plan
        self.amount = amount
        self.start_date = start_date
        self.end_date = end_date
        self.remaining_usages = remaining_usages
        self.paid = paid  # Set the paid attribute
        self.paystack_subscription_id = paystack_subscription_id
        self.user_id = user_id

    def __repr__(self):
        return f"<Subscription {self.plan} - User {self.user_id}>"
