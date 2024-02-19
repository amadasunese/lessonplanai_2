from flask import Blueprint, render_template, redirect, flash, url_for, request, session
from flask_login import login_required
from src.utils.decorators import check_is_confirmed, check_is_subscribed
from src.accounts.forms import LoginForm, RegisterForm, LessonPlanForm, ContactForm
from flask_login import login_required, login_user, logout_user, current_user
from openai import OpenAI
from markupsafe import Markup
from src.accounts.models import db, User, Subscription
from datetime import datetime, timedelta
from paystackapi.paystack import Paystack
from flask_wtf import CSRFProtect
from src.utils.decorators import logout_required
from src import bcrypt
from dotenv import load_dotenv
import os


core_bp = Blueprint("core", __name__)

load_dotenv()
PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')
# PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY')
paystack = Paystack(secret_key=PAYSTACK_SECRET_KEY)

client = OpenAI()

@core_bp.route("/")
@login_required
@check_is_confirmed
def home():
    return render_template("core/index.html")


@core_bp.route('/generate_lesson', methods=['GET', 'POST'])
@login_required
@check_is_confirmed
@check_is_subscribed
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
        """
        Convert line breaks to HTML paragraphs
        """
        lesson_content = Markup('<p>' + '</p><p>'.join(text_content.split('\n\n')) + '</p>')
        
    return render_template('core/generate_lesson.html', form=form, lesson_content=lesson_content)


@core_bp.route('/admin_users')
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
    """
    Get the user's subscription information
    """
    current_user.subscription = None
    if current_user.subscription:
        current_user.subscription = {
            'plan': current_user.subscription.plan,
            'amount': current_user.subscription.amount,
            'start_date': current_user.subscription.start_date.strftime('%Y-%m-%d %H:%M:%S'),
            'end_date': current_user.subscription.end_date.strftime('%Y-%m-%d %H:%M:%S'),
            'remaining_usages': current_user.subscription.remaining_usages,
            'paystack_subscription_id': current_user.subscription.paystack_subscription_id
        }
    return render_template('accounts/dashboard.html', user=current_user)

# Subscription model configuration
plans = {
    'starter': {'name': 'Starter Plan', 'cost': 2000, 'duration': 1, 'usage_limit': 2},
    'basic': {'name': 'Basic Plan', 'cost': 5000, 'duration': 7, 'usage_limit': 4},
    'premium': {'name': 'Premium Plan', 'cost': 10000, 'duration': 30, 'usage_limit': None}
}

@core_bp.route('/subscribe', methods=['GET', 'POST'])
@login_required
def subscribe():
    user_info = {
        'email': current_user.email,
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
    }

    if request.method == 'POST':
        selected_plan = request.form.get('selectedPlan')
        if selected_plan not in plans:
            flash('Invalid subscription plan selected.', 'danger')
            return redirect(url_for('accounts.subscribe'))

        try:
            """
            Create Paystack subscription
            """
            subscription_response = paystack.subscription.create(
                customer=current_user.email,
                plan=plans[selected_plan],
                authorization=paystack
            )

            if subscription_response['status']:
                """
                Create Subscription model instance
                """
                subscription = Subscription(
                    plan=selected_plan,
                    amount=plans[selected_plan]['cost'],
                    start_date=datetime.utcnow(),
                    end_date=datetime.utcnow() + timedelta(days=plans[selected_plan]['duration']),
                    remaining_usages=plans[selected_plan]['usage_limit'],
                    user_id=current_user.id,
                    paystack_subscription_id=subscription_response['data']['id'],
                )

                db.session.add(subscription)
                db.session.commit()

                flash('Subscription successful!', 'success')
                return redirect(url_for('accounts.dashboard'))
            else:
                flash('Paystack subscription creation failed.', 'danger')

        except Exception as e:
            flash(f'Subscription creation failed: {str(e)}', 'danger')
            db.session.rollback() 

        return redirect(url_for('accounts.subscribe'))

    plans_list = [(plan_id, plans[plan_id]) for plan_id in plans]

    return render_template('accounts/subscribe.html', user=current_user, plans=plans_list, user_info=user_info)


# Admin user configuration
@core_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied: You must be an admin to view this page.', 'danger')
        return redirect(url_for('core/index'))
    return render_template('core/admin_dashboard.html')


@core_bp.route('/delete_user/<int:user_id>')
@login_required  
def delete_user(user_id):
    user_to_delete = User.query.get(user_id)
    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User successfully removed', 'success')
    else:
        flash('User not found', 'error')
    return redirect(url_for('core/admin_dashboard'))  