from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


db = SQLAlchemy()

# class User(db.Model, UserMixin):
#     """
#     user model database
#     """
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100))
#     sex = db.Column(db.String(10))
#     age = db.Column(db.Integer)
#     profession = db.Column(db.String(100))
#     phone_number = db.Column(db.String(20))
#     email = db.Column(db.String(100), unique=True, nullable=False)
#     password = db.Column(db.String(60), nullable=False)
#     is_admin = db.Column(db.Boolean, default=False)
#     @property
#     def is_admin_property(self):
#         # This property can be used to easily check if a user is an admin in the templates.
#         return self.is_admin


class User(db.Model, UserMixin):
    """
    User model for the database
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    sex = db.Column(db.String(10))
    age = db.Column(db.Integer)
    profession = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    email_confirmed = db.Column(db.Boolean, default=False)
    confirmation_token = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)

    @property
    def is_admin_property(self):
        # This property can be used to easily check if a user is an admin in the templates.
        return self.is_admin

    def __init__(self, name, email, phone_number, sex, age, profession, password, is_admin=False):
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.sex = sex
        self.age = age
        self.profession = profession
        self.password = password
        self.is_admin = is_admin