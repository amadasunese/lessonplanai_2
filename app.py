#!/usr/bin/env python3
"""
School Lesson Plan Writer application
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

import os
import openai
# from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
# from markupsafe import Markup
from openai import OpenAI
# import smtplib

from models import db, User
from views import main
from itsdangerous import URLSafeTimedSerializer

from flask_wtf.csrf import CSRFProtect
from flask_wtf import CSRFProtect
from flask_mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a97380abc78efeea392f4af3a04339ee'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
csrf = CSRFProtect(app)
mail = Mail(app)

serializer = URLSafeTimedSerializer(app.secret_key)

# Initialize db in the app context
#db = SQLAlchemy(app)

# db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

#openai.api_key = os.getenv("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")
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

# Initialize migrate with your Flask app and SQLAlchemy DB
migrate = Migrate(app, db)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

db.init_app(app)

app.register_blueprint(main)


app.static_folder = 'static'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
