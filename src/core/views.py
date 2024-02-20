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

from paystackapi.transaction import Transaction



core_bp = Blueprint("core", __name__)

load_dotenv()
PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')
PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY')
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


# @core_bp.route('/admin_users')
# @login_required
# def manage_users():
#     if not current_user.is_admin:
#         flash('Access denied: You must be an admin to view this page.', 'danger')
#         return redirect(url_for('core/index'))
#     users = User.query.all()
#     return render_template('core/manage_users.html', users=users)


from sqlalchemy.orm import joinedload

@core_bp.route('/admin_users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('Access denied: You must be an admin to view this page.', 'danger')
        return redirect(url_for('core.index'))

    # Query users with subscriptions
    users_with_subscriptions = User.query.options(joinedload(User.subscription)).all()

    return render_template('core/manage_users.html', users=users_with_subscriptions)




@core_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Get the user's subscription information
    """
    subscription = Subscription.query.filter_by(user_id=current_user.id).first()
    return render_template('accounts/dashboard.html', subscription=subscription)

# Subscription model configuration
plans = {
    'starter': {'name': 'Starter Plan', 'cost': 2000, 'duration': 1, 'usage_limit': 2},
    'basic': {'name': 'Basic Plan', 'cost': 5000, 'duration': 7, 'usage_limit': 4},
    'premium': {'name': 'Premium Plan', 'cost': 10000, 'duration': 30, 'usage_limit': None}
}

@core_bp.route('/subscribe', methods=['GET', 'POST'])
@login_required
def subscribe():
    # user_info = {
    #     'email': current_user.email,
    #     'first_name': current_user.first_name,
    #     'last_name': current_user.last_name,
    # }

    # if request.method == 'POST':
    #     selected_plan = request.form.get('selectedPlan')
    #     if selected_plan not in plans:
    #         flash('Invalid subscription plan selected.', 'danger')
    #         return redirect(url_for('accounts.subscribe'))

    #     try:
    #         """
    #         Create Paystack subscription
    #         """
    #         subscription_response = paystack.subscription.create(
    #             customer=current_user.email,
    #             plan=plans[selected_plan],
    #             authorization=paystack
    #         )

    #         if subscription_response['status']:
    #             """
    #             Create Subscription model instance
    #             """
    #             subscription = Subscription(
    #                 plan=selected_plan,
    #                 amount=plans[selected_plan]['cost'],
    #                 start_date=datetime.utcnow(),
    #                 end_date=datetime.utcnow() + timedelta(days=plans[selected_plan]['duration']),
    #                 remaining_usages=plans[selected_plan]['usage_limit'],
    #                 user_id=current_user.id,
    #                 paystack_subscription_id=subscription_response['data']['id'],
    #             )

    #             db.session.add(subscription)
    #             db.session.commit()

    #             flash('Subscription successful!', 'success')
    #             return redirect(url_for('accounts.dashboard'))
    #         else:
    #             flash('Paystack subscription creation failed.', 'danger')

    #     except Exception as e:
    #         flash(f'Subscription creation failed: {str(e)}', 'danger')
    #         db.session.rollback() 

    #     return redirect(url_for('accounts.subscribe'))

    # plans_list = [(plan_id, plans[plan_id]) for plan_id in plans]

    return render_template('accounts/subscribe.html') # , user=current_user, plans=plans_list, user_info=user_info


# Admin user configuration
@core_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied: You must be an admin to view this page.', 'danger')
        return redirect(url_for('core.home'))
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
    return redirect(url_for('core.manager_users'))  

# Payment processing routes

@core_bp.route('/subscribe_starter', methods=['GET', 'POST'])
@login_required
def subscribe_starter():
    plan = 'Starter'
    amount = '20000'
    first_name = current_user.first_name
    last_name = current_user.last_name
    email = current_user.email

    response = Transaction.initialize(amount=amount, email=email)

    ref = response.get('data', {}).get('reference')
    print(f"{first_name} {last_name}")
    
    create_subscription_instance = Subscription(
        plan='Starter',
        amount=2000,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=plans['starter']['duration']),
        remaining_usages=plans['starter']['usage_limit'],
        paid=True,  # Set paid to True for a successful payment
        user_id=current_user.id,
        paystack_subscription_id=response.get('data', {}).get('reference')
    )

    db.session.add(create_subscription_instance)
    db.session.commit()

    a_url = response['data']['authorization_url']
    return redirect(a_url)

@core_bp.route('/subscribe_basic', methods=['GET', 'POST'])
@login_required
def subscribe_basic():
    amount = '5000'
    first_name = current_user.first_name
    last_name = current_user.last_name
    email = current_user.email

    response = Transaction.initialize(amount=amount, email=email)

    ref = response['data']['reference']
    print(f"{first_name} {last_name}")
    # create_pay_instance = Subscription(current_user_name=first_name, customers_email=email,
    #                                                plan='Starter', reference=ref, amount='2000')
    
    create_subscription_instance = Subscription(
        plan='Starter',
        amount=5000,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=plans['basic']['duration']),
        remaining_usages=plans['basic']['usage_limit'],
        paid=True,  # Set paid to True for a successful payment
        user_id=current_user.id,
        paystack_subscription_id=response['data']['reference']
    )
    db.session.add(create_subscription_instance)
    db.session.commit()

    # flash('Subscription successful!', 'success')
    # return render_template('core/admin_dashboard.html')

    a_url = response['data']['authorization_url']
    return redirect(a_url)

@core_bp.route('/subscribe_premium', methods=['GET', 'POST'])
@login_required
def subscribe_premium():
    amount = '10000'
    first_name = current_user.first_name
    last_name = current_user.last_name
    email = current_user.email

    response = Transaction.initialize(amount=amount, email=email)

    ref = response['data']['reference']
    print(f"{first_name} {last_name}")
    
    create_subscription_instance = Subscription(
        plan='Starter',
        amount=10000,
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow() + timedelta(days=plans['premium']['duration']),
        remaining_usages=plans['premium']['usage_limit'],
        paid=True,  # Set paid to True for a successful payment
        user_id=current_user.id,
        paystack_subscription_id=response['data']['reference']
    )
    db.session.add(create_subscription_instance)
    db.session.commit()

    # flash('Subscription successful!', 'success')
    # return render_template('core/admin_dashboard.html')

    a_url = response['data']['authorization_url']
    return redirect(a_url)



@core_bp.route('/verify_payment', methods=['GET', 'POST'])
@login_required
def verify_payment():
    paramz = request.args.get('trxref', 'None')  # Use request.args to get query parameters
    first_name = current_user.first_name
    last_name = current_user.last_name
    email = current_user.email
    print(paramz)
    
    # Assuming you have a method to verify the payment in your Transaction class
    details = Transaction.verify(reference=paramz)
    status = details['data']['status']
    
    if status == 'success':
        pay_instance = Subscription.query.filter_by(paystack_subscription_id=paramz).first()
        if pay_instance:
            if pay_instance.plan == 'Starter':
                expiry_date = pay_instance.start_date + timedelta(days=1)
            elif pay_instance.plan == 'Basic':
                expiry_date = pay_instance.start_date + timedelta(days=7)
            elif pay_instance.plan == 'Premium':
                expiry_date = pay_instance.start_date + timedelta(days=30)

            pay_instance.update(paid=True, end_date=expiry_date)

            # Update the user subscription details
            current_user.update(subscribed=True, expiry_date=expiry_date)
            print('Payment successful!')
        else:
            print('Subscription not found for the given transaction reference.')

    else:
        print('Payment not successful')

    return redirect('core.dashboard')