from flask import Blueprint, render_template, redirect, flash, url_for
from flask_login import login_required
from src.utils.decorators import check_is_confirmed
from src.accounts.forms import LoginForm, RegisterForm, LessonPlanForm, ContactForm
from flask_login import login_required, login_user, logout_user, current_user
from openai import OpenAI
from markupsafe import Markup
from models import db, User

core_bp = Blueprint("core", __name__)

client = OpenAI()

@core_bp.route("/")
# @login_required
# @check_is_confirmed
def home():
    return render_template("core/index.html")


@core_bp.route('/generate_lesson', methods=['GET', 'POST'])
@login_required
@check_is_confirmed
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
        
    return render_template('core/generate_lesson.html', form=form, lesson_content=lesson_content)


@core_bp.route('/admin/users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('Access denied: You must be an admin to view this page.', 'danger')
        return redirect(url_for('core/index'))
    users = User.query.all()
    return render_template('core/manage_users.html', users=users)


@core_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('accounts/dashboard.html', name=current_user.email)



@core_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied: You must be an admin to view this page.', 'danger')
        return redirect(url_for('core/index'))
    # You could pass in more data here if needed
    return render_template('core/admin_dashboard.html')


@core_bp.route('/delete_user/<int:user_id>')
# @login_required  
def delete_user(user_id):
    user_to_delete = User.query.get(user_id)
    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User successfully removed', 'success')
    else:
        flash('User not found', 'error')
    return redirect(url_for('core/admin_dashboard'))  







# @core_bp.route('/admin/remove_user/<int:user_id>', methods=['POST'])
# @login_required
# def remove_user(user_id):
#     if not current_user.is_admin:
#         flash('Access denied: You must be an admin to perform this action.', 'danger')
#         return redirect(url_for('main.index'))
    
#     user_to_remove = User.query.get_or_404(user_id)
#     db.session.delete(user_to_remove)
#     db.session.commit()
#     flash('User removed successfully.', 'success')
#     return redirect(url_for('main.manage_users'))










# @core_bp.route('/admin/manage_services')
# @login_required
# def manage_services():
#     if not current_user.is_admin:
#         flash('Access denied: You must be an admin to view this page.', 'danger')
#         return redirect(url_for('core/index'))
#     # Query your services from the database
#     services = Service.query.all() # Assuming you have a Service model
#     return render_template('core/manage_services.html', services=services)

# # Add service route example
# @core_bp.route('/admin/add_service', methods=['GET', 'POST'])
# @login_required
# def add_service():
#     if not current_user.is_admin:
#         flash('Access denied: You must be an admin to view this page.', 'danger')
#         return redirect(url_for('core/admin_dashboard'))
#     # Handle GET to show a form and POST to save the new service
    # ...

# # Edit service route example
# @core_bp.route('/admin/edit_service/<int:service_id>', methods=['GET', 'POST'])
# @login_required
# def edit_service(service_id):
#     if not current_user.is_admin:
#         flash('Access denied: You must be an admin to view this page.', 'danger')
#         return redirect(url_for('core/admin_dashboard'))
#     # Handle GET to show the service data and POST to update the service
#     # ...

# # Delete service route example
# @core_bp.route('/admin/delete_service/<int:service_id>', methods=['POST'])
# @login_required
# def delete_service(service_id):
#     if not current_user.is_admin:
#         flash('Access denied: You must be an admin to perform this action.', 'danger')
#         return redirect(url_for('core/admin_dashboard'))
#     # Handle POST to delete the service
    # ...