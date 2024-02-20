from flask import flash
from src import app
from src.accounts.models import db, User
from werkzeug.security import generate_password_hash
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt


def add_admin(first_name, last_name, email, password):
    with app.app_context():
        if isinstance(password, bytes):
            password = password.decode('utf-8')

        # hashed_password = generate_password_hash(password) # .decode('utf-8')

        admin_user = User(first_name=first_name, last_name=last_name, email=email,
                          password=password, is_admin=True)
        db.session.add(admin_user)
        db.session.commit()


if __name__ == "__main__":
    first_name = input("Enter admin first name: ")
    last_name = input("Enter admin last name: ")
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")
    add_admin(first_name, last_name, email, password)
