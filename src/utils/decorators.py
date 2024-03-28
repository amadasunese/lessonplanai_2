from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user
from src.accounts.models import Parent, Tutor
from datetime import datetime


def logout_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            flash("You are already authenticated.", "info")
            return redirect(url_for("core.home"))
        return func(*args, **kwargs)

    return decorated_function

def check_is_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_confirmed is False:
            flash("Please confirm your account!", "warning")
            return redirect(url_for("accounts.inactive"))
        return func(*args, **kwargs)

    return decorated_function


# def check_is_subscribed(func):
#     @wraps(func)
#     def decorated_function(*args, **kwargs):
#         if not current_user.subscription or current_user.subscription.end_date < datetime.utcnow():
#             flash("Please subscribe to use this service", "warning")
#             return redirect(url_for("core.subscribe"))
#         return func(*args, **kwargs)

#     return decorated_function

# def check_is_subscribed(func):
#     @wraps(func)
#     def decorated_function(*args, **kwargs):
#         if not current_user.subscription or \
#            current_user.subscription.end_date < datetime.utcnow() or \
#            current_user.subscription.paid != 'yes':
#             flash("Please subscribe to use this service", "warning")
#             return redirect(url_for("core.subscribe"))
#         return func(*args, **kwargs)

#     return decorated_function

def check_is_subscribed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        subscription = getattr(current_user, 'subscription', None)
        if subscription is None or \
           subscription.end_date < datetime.utcnow() or \
           subscription.paid != 'yes':
            flash("Please subscribe to use this service", "warning")
            return redirect(url_for("core.subscribe"))
        return func(*args, **kwargs)
    return decorated_function

def is_parent(user_id):
    # This function checks if a parent with the given user_id exists
    return Parent.query.filter_by(user_id=user_id).first() is not None

def check_is_registered(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not is_parent(current_user.id):
            flash('You need to be registered as a parent to use this service.', 'warning')
            return redirect(url_for('core.register_parent'))
        return func(*args, **kwargs)
    return decorated_function

def is_tutor(user_id):
    # This function checks if a tutor with the given user_id exists
    return Tutor.query.filter_by(user_id=user_id).first() is not None

def check_is_tutor_registered(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not is_tutor(current_user.id):
            flash('You need to be registered as a tutor to use this service.', 'warning')
            return redirect(url_for('core.tutor_registration'))
        return func(*args, **kwargs)
    return decorated_function