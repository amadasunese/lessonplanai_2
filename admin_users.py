from flask import Flask, render_template, request, redirect, url_for, flash
from flask import flash
from src import app
from src.accounts.models import db, User
from werkzeug.security import generate_password_hash
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt



# import pandas as pd
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.naive_bayes import MultinomialNB
# from nltk.corpus import stopwords
# from nltk.stem import PorterStemmer
# import joblib
# from form import ContactForm
# from flask_mail import Mail, Message
# import smtplib
# # from decouple import config
# from dotenv import load_dotenv
# import os
# from config import config

app = Flask(__name__)


def add_admin(first_name, last_name, email, password):
    with app.app_context():
        if isinstance(password, bytes):
            password = password.decode('utf-8')

        # hashed_password = generate_password_hash(password) # .decode('utf-8')

        admin_user = User(first_name=first_name, last_name=last_name, email=email,
                          password=password, is_admin=True)
        db.session.add(admin_user)
        db.session.commit()
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)

    # first_name = input("Enter admin first name: ")
    # last_name = input("Enter admin last name: ")
    # email = input("Enter admin email: ")
    # password = input("Enter admin password: ")
    # add_admin(first_name, last_name, email, password)
