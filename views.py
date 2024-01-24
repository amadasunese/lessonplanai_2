from flask import Flask, render_template, redirect, url_for, flash, Blueprint, session
from wtforms.validators import DataRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
import openai
from flask import request
from flask_wtf.csrf import CSRFProtect
from flask_wtf import CSRFProtect
import smtplib
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from forms import RegistrationForm, LoginForm, LessonPlanForm, ContactForm
from markupsafe import Markup
import smtplib
from models import db, User
import openai
from openai import OpenAI
# from flask_security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a97380abc78efeea392f4af3a04339ee'
# ... (other imports)

# Assuming you have a User and db model already defined

# Configure Flask-Mail
mail = Mail()

# Configure Flask-Security
# user_datastore = SQLAlchemyUserDatastore(db, User, Role)
# security = Security(app, user_datastore)

# Configure Flask-Security email confirmation
# serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
serializer = URLSafeTimedSerializer(app.secret_key)



main = Blueprint('main', __name__)

# Configure your email settings
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'amadasunese@gmail.com'
EMAIL_HOST_PASSWORD = 'qxxo axga dzia jjsw'
RECIPIENT_ADDRESS = 'amadasunese@gmail.com'
mail = Mail(app)

@main.route('/')
def index():
    return render_template('index.html')


client = OpenAI()

# Initialize CSRFProtect
csrf = CSRFProtect(app)



@main.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check for existing user with the same email
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered. Please choose a different email or reset your password if you have forgotten it.', 'danger')
            return redirect(url_for('main.signup'))

        # Generate a unique confirmation token
        token = serializer.dumps(form.email.data, salt='email-confirm')

        # Create a new user with email unconfirmed
        new_user = User(
            name=form.name.data,
            sex=form.sex.data,
            age=form.age.data,
            profession=form.profession.data,
            phone_number=form.phone_number.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data),
            # email_confirmed=False,  # Set email_confirmed to False initially
            # confirmation_token=token  # Store the token in the database
        )
        db.session.add(new_user)
        try:
            db.session.commit()  # Attempt to commit changes
        except IntegrityError:
            db.session.rollback()  # Rollback if integrity error occurs
            flash('An error occurred while creating your account. Please try again.', 'danger')
            return redirect(url_for('main.signup'))

        # Send confirmation email
        send_confirmation_email(new_user.email, token)

        flash('A confirmation email has been sent to your email address. Please confirm your email to complete registration.', 'info')
        return redirect(url_for('main.login'))

    return render_template('signup.html', form=form)


def send_confirmation_email(email, token):
    """Sends an email with a confirmation link to the specified email address."""
    subject = 'Confirm Your Email'
    confirm_url = url_for('main.confirm_email', token=token, _external=True)  # Generate external URL
    body = render_template('email/confirm_email.html', confirm_url=confirm_url)  # Use a template for flexibility
    email_message = Message(subject=subject, recipients=[email], body=body)
    # mail.send(email_message)
    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.ehlo()
        server.starttls()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.sendmail(EMAIL_HOST_USER, RECIPIENT_ADDRESS, email_message)
        server.close()
        return 'Sent successfully!'
    except Exception as e:
        return str(e)
        return redirect(url_for('home'))



@main.route('/confirm/<token>')
def confirm_email(token):
    """Confirms a user's email using a confirmation token."""
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=3600)  # Decode token and set expiration
        user = User.query.filter_by(email=email).first()
        if user:
            user.email_confirmed = True
            db.session.commit()
            flash('Email confirmed successfully. You can now log in.', 'success')
        else:
            flash('Invalid token or user not found.', 'danger')
    except Exception as e:
        app.logger.error(e)  # Log errors for debugging
        flash('Error confirming email. Please try again.', 'danger')
    return redirect(url_for('main.login'))


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            # return redirect(url_for('main.dashboard'))
        
        # Check if user is admin
        if user.is_admin:
                session['is_admin'] = True
                flash('Admin login successful', 'success')
                return redirect(url_for('main.admin_dashboard'))
        else:
            session['is_admin'] = False
            flash('Login successful', 'success')

        return redirect(url_for('main.dashboard'))
    
    else:
        flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', form=form)









# @app.route('/contact', methods=['GET', 'POST'])
# def contact():
#     if request.method == 'POST':
#         # Handle the form submission, send an email, store in DB, etc.
#         pass
#     return render_template('contact.html')


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        # Handle the form submission, e.g., send an email
        name = form.name.data
        email = form.email.data
        message = form.message.data

        # Process the data as needed
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
            return redirect(url_for('home'))

    return render_template('contact.html', form=form)

@main.route('/send_feedback', methods=['POST'])
def send_feedback():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # Email message setup
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
        return redirect(url_for('home'))
    


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.name)

# @app.route('/generate_lesson', methods=['GET', 'POST'])
# @login_required
# def generate_lesson():
#     form = LessonPlanForm()
#     lesson_content = None
#     if form.validate_on_submit():
#         response = openai.ChatCompletion.create(
#             model="gpt-4",
#             messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": form.prompt.data}],
#             temperature=0,
#             max_tokens=2048
#         )
#         lesson_content = response.choices[0].message['content']
#     return render_template('generate_lesson.html', form=form, lesson_content=lesson_content)

# @app.route('/generate_lesson', methods=['GET', 'POST'])
# @login_required
# def generate_lesson():
#     form = LessonPlanForm()
#     lesson_content = None
#     if form.validate_on_submit():
#         response = openai.ChatCompletion.create(
#             model="gpt-4",
#             messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": form.prompt.data}],
#             temperature=0,
#             max_tokens=2048
#         )
#         # Ensure that the lesson plan is marked as safe content to render
#         lesson_content = Markup(response.choices[0].message['content'])
#     return render_template('generate_lesson.html', form=form, lesson_content=lesson_content)


# @app.route('/generate_lesson', methods=['GET', 'POST'])
# @login_required
# def generate_lesson():
#     form = LessonPlanForm()
#     lesson_content = None
#     if form.validate_on_submit():
#         response = openai.chat.completions.create(
#             model="gpt-4",
#             messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": form.prompt.data}],
#             temperature=0,
#             max_tokens=2048
#         )
#         text_content = response.choices[0].message.content
        
#         # Convert line breaks to HTML paragraphs
#         lesson_content = Markup('<p>' + '</p><p>'.join(text_content.split('\n\n')) + '</p>')
        
#     return render_template('generate_lesson.html', form=form, lesson_content=lesson_content)



@main.route('/generate_lesson', methods=['GET', 'POST'])
@login_required
def generate_lesson():
    form = LessonPlanForm()
    lesson_content = None
    if form.validate_on_submit():
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": form.prompt.data}],
            temperature=0,
            max_tokens=2048
        )
        text_content = response.choices[0].message.content
        
        # Convert line breaks to HTML paragraphs
        lesson_content = Markup('<p>' + '</p><p>'.join(text_content.split('\n\n')) + '</p>')
        
    return render_template('generate_lesson.html', form=form, lesson_content=lesson_content)



# @app.route('/generate_lesson', methods=['GET', 'POST'])
# @login_required
# def generate_lesson():
#     form = LessonPlanForm()
#     lesson_content = None
#     prompt = None
#     if form.validate_on_submit():
#         prompt = form.prompt.data
#         response = openai.ChatCompletion.create(
#             model="gpt-4",
#             messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}],
#             temperature=0,
#             max_tokens=2048
#         )
#         lesson_content = response.choices[0].message['content']
#     return render_template('generate_lesson.html', form=form, lesson_content=lesson_content, prompt=prompt)






@main.route('/admin/users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('Access denied: You must be an admin to view this page.', 'danger')
        return redirect(url_for('main.index'))
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@main.route('/admin/remove_user/<int:user_id>', methods=['POST'])
@login_required
def remove_user(user_id):
    if not current_user.is_admin:
        flash('Access denied: You must be an admin to perform this action.', 'danger')
        return redirect(url_for('main.index'))
    
    user_to_remove = User.query.get_or_404(user_id)
    db.session.delete(user_to_remove)
    db.session.commit()
    flash('User removed successfully.', 'success')
    return redirect(url_for('main.manage_users'))

@main.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied: You must be an admin to view this page.', 'danger')
        return redirect(url_for('main.index'))
    # You could pass in more data here if needed
    return render_template('admin_dashboard.html')

@main.route('/admin/manage_services')
@login_required
def manage_services():
    if not current_user.is_admin:
        flash('Access denied: You must be an admin to view this page.', 'danger')
        return redirect(url_for('main.index'))
    # Query your services from the database
    services = Service.query.all() # Assuming you have a Service model
    return render_template('manage_services.html', services=services)

# Add service route example
@main.route('/admin/add_service', methods=['GET', 'POST'])
@login_required
def add_service():
    if not current_user.is_admin:
        flash('Access denied: You must be an admin to view this page.', 'danger')
        return redirect(url_for('main.admin_dashboard'))
    # Handle GET to show a form and POST to save the new service
    # ...

# Edit service route example
@main.route('/admin/edit_service/<int:service_id>', methods=['GET', 'POST'])
@login_required
def edit_service(service_id):
    if not current_user.is_admin:
        flash('Access denied: You must be an admin to view this page.', 'danger')
        return redirect(url_for('main.admin_dashboard'))
    # Handle GET to show the service data and POST to update the service
    # ...

# Delete service route example
@main.route('/admin/delete_service/<int:service_id>', methods=['POST'])
@login_required
def delete_service(service_id):
    if not current_user.is_admin:
        flash('Access denied: You must be an admin to perform this action.', 'danger')
        return redirect(url_for('main.admin_dashboard'))
    # Handle POST to delete the service
    # ...
