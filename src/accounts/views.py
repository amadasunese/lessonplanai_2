from flask import Blueprint, flash, redirect, render_template, request, url_for, session
from flask_login import login_required, login_user, logout_user, current_user
from src import bcrypt, db
from src.accounts.models import User
from .forms import LoginForm, RegisterForm, LessonPlanForm, ContactForm, ResetPasswordForm, ResetPasswordRequestForm
from src.utils.decorators import logout_required
from src.accounts.token import confirm_token, generate_token
from src.utils.email import send_email, send_feedback
import openai
from openai import OpenAI
from datetime import datetime
from markupsafe import Markup
from flask_mail import Message, Mail
from src import app
import smtplib
from werkzeug.security import generate_password_hash
from itsdangerous import URLSafeTimedSerializer

accounts_bp = Blueprint("accounts", __name__)

client = OpenAI()

# Configure your email settings
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'lessonplanai@gmail.com'
EMAIL_HOST_PASSWORD = 'kyvy fwml epob tcta'
RECIPIENT_ADDRESS = 'lessonplanai@gmail.com'
mail = Mail(app)


@accounts_bp.route("/register", methods=["GET", "POST"])
@logout_required
def register():
    if current_user.is_authenticated:
        flash("You are already registered.", "info")
        return redirect(url_for("core.home"))
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()
        token = generate_token(user.email)
        confirm_url = url_for("accounts.confirm_email", token=token, _external=True)
        html = render_template("accounts/confirm_email.html", confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_email(user.email, subject, html)

        login_user(user)
        flash("You registered and are now logged in. Welcome!", "success")

        return redirect(url_for("core.home"))

    return render_template("accounts/register.html", form=form)

    

# @accounts_bp.route('/login', methods=['GET', 'POST'])
# @logout_required
# def login():
#     if current_user.is_authenticated:
#         flash("You are already logged in.", "info")
#         return redirect(url_for("core.index"))
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data).first()
#         if user and bcrypt.check_password_hash(user.password, request.form["password"]):
#             login_user(user)
#             return redirect(url_for('core.home'))
        
#         # Check if user is admin
#         if user.is_admin:
#                 session['is_admin'] = True
#                 flash('Admin login successful', 'success')
#                 return redirect(url_for('core.admin_dashboard'))
#         else:
#             session['is_admin'] = False
#             flash('Login successful', 'success')

#         return redirect(url_for('accounts/dashboard'))
    
#     else:
#         flash('Login Unsuccessful. Please check email and password', 'danger')

#     return render_template('core/landing_page.html', form=form)


@accounts_bp.route('/login', methods=['GET', 'POST'])
@logout_required
def login():
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for("core.index"))
    
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)

            if user.is_admin:
                session['is_admin'] = True
                flash('Admin login successful', 'success')
                return redirect(url_for('core.admin_dashboard'))
            else:
                session['is_admin'] = False
                flash('Login successful', 'success')
                return redirect(url_for('core.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('core/landing_page.html', form=form)


@accounts_bp.route("/confirm/<token>")
@login_required
def confirm_email(token):
    if current_user.is_confirmed:
        flash("Account already confirmed.", "success")
        return redirect(url_for("core.home"))
    email = confirm_token(token)
    user = User.query.filter_by(email=current_user.email).first_or_404()
    if user.email == email:
        user.is_confirmed = True
        user.confirmed_on = datetime.now()
        db.session.add(user)
        db.session.commit()
        flash("You have confirmed your account. Thanks!", "success")
    else:
        flash("The confirmation link is invalid or has expired.", "danger")
    return redirect(url_for("core.home"))


@accounts_bp.route("/inactive")
@login_required
def inactive():
    if current_user.is_confirmed:
        return redirect(url_for("core.home"))
    return render_template("accounts/inactive.html")

@accounts_bp.route("/resend")
@login_required
def resend_confirmation():
    if current_user.is_confirmed:
        flash("Your account has already been confirmed.", "success")
        return redirect(url_for("core.home"))
    token = generate_token(current_user.email)
    confirm_url = url_for("accounts.confirm_email", token=token, _external=True)
    html = render_template("accounts/confirm_email.html", confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_email(current_user.email, subject, html)
    flash("A new confirmation email has been sent.", "success")
    return redirect(url_for("accounts.inactive"))


@accounts_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You were logged out.", "success")
    return redirect(url_for("accounts.login"))


@accounts_bp.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        """
        Handle the form submission, e.g., send an email
        """
        name = form.name.data
        email = form.email.data
        message = form.message.data
        
        """
        Process the data as needed
        """
        email_message = f"Subject: Feedback from {name}\n\nFrom: {email}\n\nMessage: {message}"

        # Sending the email
        try:
            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
            server.ehlo()
            server.starttls()
            server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
            server.sendmail(EMAIL_HOST_USER, RECIPIENT_ADDRESS, email_message)
            server.close()
            return 'Feedback sent successfully!'
        except Exception as e:
            return str(e)
            return redirect(url_for('core.home'))

    return render_template('accounts/contact.html', form=form)


# from here
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

def send_password_reset_email(user):
    """Password reset email
    """
    token = s.dumps(user.email, salt='password-reset-salt')
    msg = Message('Reset Your Password', sender='lessonplanai@gmail.com',
                  recipients=[user.email])
    msg.body = (
        f"To reset your password, visit the following link: "
        f"{url_for('accounts.reset_password', token=token, _external=True)}"
    )
    mail.send(msg)


@accounts_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """Process password reset request
    """
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Password reset email sent if your email is in our system.')
        return redirect(url_for('accounts.login'))
    return render_template('accounts/reset_password_request.html',
                           title='Reset Password', form=form)


@accounts_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except Exception:
        flash('The password reset link is invalid or has expired.')
        return redirect(url_for('accounts.reset_password_request'))

    user = User.query.filter_by(email=email).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('accounts.reset_password_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Update user's password
        user.password_hash = bcrypt.generate_password_hash(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('accounts.login'))
    return render_template('accounts/reset_password.html',
                           title='Reset Password', form=form, token=token)
