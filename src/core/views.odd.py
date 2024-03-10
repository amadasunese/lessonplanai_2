from flask import Blueprint, render_template, redirect, flash, url_for, request
from flask_login import login_required
from src.utils.decorators import check_is_confirmed, check_is_subscribed, check_is_registered
from src.accounts.forms import LessonPlanForm, ParentRegistrationForm
from flask_login import login_required, current_user
from openai import OpenAI
from markupsafe import Markup
from src.accounts.models import db, User, Subscription, Tutor, TutorFeePayment, Parent
from datetime import datetime, timedelta
from paystackapi.paystack import Paystack
from flask_wtf import CSRFProtect
from src.utils.decorators import logout_required
from src import bcrypt
from dotenv import load_dotenv
import os
from paystackapi.transaction import Transaction
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename
from src.utils.plan import plans
from flask import request, jsonify
from datetime import datetime, timedelta
import requests



core_bp = Blueprint("core", __name__)

load_dotenv()
PAYSTACK_SECRET_KEY = os.environ.get('PAYSTACK_SECRET_KEY')
PAYSTACK_PUBLIC_KEY = os.environ.get('PAYSTACK_PUBLIC_KEY')
paystack = Paystack(secret_key=PAYSTACK_SECRET_KEY)

client = OpenAI()

#################################
#      Navigation routes        #
#################################

@core_bp.route("/")
@login_required
# @check_is_confirmed
def home():
    return render_template("core/index.html")

@core_bp.route('/online_tutor', methods=['GET', 'POST'])
@login_required
def online_tutor():
    return render_template('accounts/online_tutor.html') 


@core_bp.route('/hire_tutor', methods=['GET', 'POST'])
@login_required
def hire_tutor():
    return render_template('accounts/hire_tutor.html') 


@core_bp.route('/tutor_exploration', methods=['GET', 'POST'])
@login_required
def tutor_exploration():
    return render_template('accounts/tutor_exploration.html')


@core_bp.route('/about', methods=['GET', 'POST'])
@login_required
def about():
    return render_template('accounts/about.html')


@core_bp.route('/faq', methods=['GET', 'POST'])
@login_required
def faq():
    return render_template('accounts/faq.html')


@core_bp.route('/subscribe', methods=['GET', 'POST'])
@login_required
def subscribe():
    return render_template('accounts/subscribe.html')


#################################
# Lesson plan generation routes #
#################################

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


#################################
#   Admin login users routes     #
#################################

@core_bp.route('/admin_users')
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('Access denied: You must be an admin to view this page.', 'danger')
        return redirect(url_for('core.index'))

    """Query users with subscriptions"""
    users_with_subscriptions = User.query.options(joinedload(User.subscription)).all()

    return render_template('core/manage_users.html', users=users_with_subscriptions)


# Subscription model configuration
plans = {
    'starter': {'name': 'Starter Plan', 'cost': 2000, 'duration': 1, 'usage_limit': 2},
    'basic': {'name': 'Basic Plan', 'cost': 5000, 'duration': 7, 'usage_limit': 4},
    'premium': {'name': 'Premium Plan', 'cost': 10000, 'duration': 30, 'usage_limit': None}
}


# Admin user configuration
@core_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied: You must be an admin to view this page.', 'danger')
        return redirect(url_for('core.home'))
    return render_template('core/admin_dashboard.html')


@core_bp.route('/dashboard')
@login_required
@check_is_confirmed
def dashboard():
    """
    Get the user's subscription information
    """
    subscription = Subscription.query.filter_by(user_id=current_user.id).first()
    return render_template('accounts/dashboard.html', subscription=subscription, today=datetime.now())


#################################
#   Users management routes     #
#################################

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


@core_bp.route('/delete_tutor/<int:tutor_id>')
@login_required  
def delete_tutor(tutor_id):
    tutor_to_delete = Tutor.query.get(tutor_id)
    if tutor_to_delete:
        db.session.delete(tutor_to_delete)
        db.session.commit()
        flash('Tutor successfully removed', 'success')
    else:
        flash('Tutor not found', 'error')
    return redirect(url_for('core.manage_users')) 


@core_bp.route('/delete_parent/<int:parent_id>')
@login_required  
def delete_parent(parent_id):
    parent_to_delete = Parent.query.get(parent_id)
    if parent_to_delete:
        db.session.delete(parent_to_delete)
        db.session.commit()
        flash('Parent successfully removed', 'success')
    else:
        flash('Parent not found', 'error')
    return redirect(url_for('core.registered_parent'))


# @core_bp.route('/delete_subscribed_user/<int:subscription_id>')
# @login_required  
# def delete_subscribed_user(subscription_id):
#     user_to_delete = Subscription.query.get(subscription_id)
#     if user_to_delete:
#         db.session.delete(user_to_delete)
#         db.session.commit()
#         flash('User successfully removed', 'success')
#     else:
#         flash('User not found', 'error')
#     return redirect(url_for('core.subscribed_users')) 


# @core_bp.route('/delete_subscription/<int:subscription_id>', methods=['POST'])
# @login_required
# def delete_subscription(subscription_id):
#     # Find the subscription by ID
#     subscription = Subscription.query.get(subscription_id)

#     if subscription is None:
#         # Handle the case where the subscription does not exist
#         flash('Subscription not found.', 'error')
#         return redirect(url_for('some_route'))

#     if subscription.user_id != current_user.id:
#         # Ensure that the current user owns the subscription or has the right to delete it
#         flash('You do not have permission to delete this subscription.', 'error')
#         return redirect(url_for('some_route'))

#     # Delete the subscription
#     db.session.delete(subscription)
#     db.session.commit()

#     flash('Subscription deleted successfully.', 'success')
#     return redirect(url_for('some_route'))



@core_bp.route('/edit-tutor/<int:tutor_id>', methods=['GET', 'POST'])
def edit_tutor(tutor_id):
    """
    Retrieve the existing tutor from the database
    """
    tutor = Tutor.query.get_or_404(tutor_id)

    if request.method == 'POST':
        """Handle form submission for editing"""
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        address = request.form['address']
        phone_number = request.form['phone_number']
        age = request.form['age']
        education_qualification = request.form['education_qualification']
        interest = request.form['interest']
        subjects = request.form['subjects']
        past_experience = 'past_experience' in request.form
        experience_years = request.form['experience_years']
        experience_description = request.form['experience_description']
        interest_join = request.form['interest_join']
        languages = request.form['languages']
        availability = request.form['availability']
        teaching_mode = request.form['teaching_mode']
        student_level = request.form['student_level']
        source = request.form['source']
        confirmation_name = request.form['confirmation_name']
        photo = request.files['photo']

        db.session.commit()

        flash('Tutor information updated successfully!', 'success')
        return redirect(url_for('core.tutor_list'))

    """Render the form for editing with pre-filled data"""
    return render_template('core/edit_tutor.html', tutor=tutor)


# @core_bp.route('/tutor_list', methods=['GET', 'POST'])
# @login_required
# def tutor_list():
#     return render_template('core/tutor_list.html')


######################################
#   Subscription & payment routes    #
######################################

# @core_bp.route('/subscribe_starter', methods=['GET', 'POST'])
# @login_required
# def subscribe_starter():
#     plan = 'Starter'
#     amount = '20000'
#     email = current_user.email

#     response = Transaction.initialize(amount=amount, email=email)
#     print(response)
#     ref = response.get('data', {}).get('reference')
#     print(ref)

#     create_subscription_instance = Subscription(
#         plan='Starter',
#         amount=2000,
#         start_date=datetime.utcnow(),
#         end_date=datetime.utcnow() + timedelta(days=plans['starter']['duration']),
#         remaining_usages=plans['starter']['usage_limit'],
#         paid=False,
#         user_id=current_user.id,
#         paystack_subscription_id=ref
#     )

#     db.session.add(create_subscription_instance)
#     db.session.commit()

#     a_url = response['data']['authorization_url']
#     return redirect(a_url)


# @core_bp.route('/subscribe_basic', methods=['GET', 'POST'])
# @login_required
# def subscribe_basic():
#     plan = 'Basic'
#     amount = '5000'
#     email = current_user.email

#     response = Transaction.initialize(amount=amount, email=email)
#     ref = response['data']['reference']

#     create_subscription_instance = Subscription(
#         plan='Basic',
#         amount=5000,
#         start_date=datetime.utcnow(),
#         end_date=datetime.utcnow() + timedelta(days=plans['basic']['duration']),
#         remaining_usages=plans['basic']['usage_limit'],
#         paid=False,
#         user_id=current_user.id,
#         paystack_subscription_id=ref
#     )

#     db.session.add(create_subscription_instance)
#     db.session.commit()

#     a_url = response['data']['authorization_url']
#     return redirect(a_url)


# @core_bp.route('/subscribe_premium', methods=['GET', 'POST'])
# @login_required
# def subscribe_premium():
#     plan = 'Premium'
#     amount = '10000'
#     email = current_user.email

#     response = Transaction.initialize(amount=amount, email=email)
#     ref = response['data']['reference']

#     create_subscription_instance = Subscription(
#         plan=plan,
#         amount=10000,
#         start_date=datetime.utcnow(),
#         end_date=datetime.utcnow() + timedelta(days=plans['premium']['duration']),
#         remaining_usages=plans['premium']['usage_limit'],
#         paid=False,
#         user_id=current_user.id,
#         paystack_subscription_id=ref
#     )

#     db.session.add(create_subscription_instance)
#     db.session.commit()

#     a_url = response['data']['authorization_url']
#     return redirect(a_url)

@core_bp.route('/subscribe_starter', methods=['GET', 'POST'])
@login_required
def subscribe_starter():
    plan = 'Starter'
    amount = '20000'
    email = current_user.email

    response = Transaction.initialize(amount=amount, email=email)
    ref = response.get('data', {}).get('reference')

    a_url = response['data']['authorization_url']
    return redirect(a_url)


@core_bp.route('/subscribe_basic', methods=['GET', 'POST'])
@login_required
def subscribe_basic():
    plan = 'Basic'
    amount = '5000'
    email = current_user.email

    response = Transaction.initialize(amount=amount, email=email)
    ref = response['data']['reference']

    a_url = response['data']['authorization_url']
    return redirect(a_url)


@core_bp.route('/subscribe_premium', methods=['GET', 'POST'])
@login_required
def subscribe_premium():
    plan = 'Premium'
    amount = '10000'
    email = current_user.email

    response = Transaction.initialize(amount=amount, email=email)
    ref = response['data']['reference']
    print(ref)

    a_url = response['data']['authorization_url']
    print(a_url)
    return redirect(a_url)


# @core_bp.route('/payment_verification', methods=['GET', 'POST'])
# @login_required
# def payment_verification():
#     data = request.json
#     reference = data.get('reference')
#     # Verify payment with Paystack (or your payment gateway)
#     verification_response = Paystack.verify_payment(reference)
#     if verification_response['status']:  # Assuming 'status' indicates success
#         # Extract necessary information from the verification response
#         plan = verification_response['data']['plan']
#         amount = verification_response['data']['amount']
#         paystack_subscription_id = verification_response['data']['subscription_id']
        
#         # Calculate subscription dates based on plan
#         start_date = datetime.now()
#         if plan == 'Starter':
#             end_date = start_date + timedelta(days=30)  # 1 month
#             remaining_usages = 100  # Example value
#         elif plan == 'Basic':
#             end_date = start_date + timedelta(days=90)  # 3 months
#             remaining_usages = 300  # Example value
#         elif plan == 'Premium':
#             end_date = start_date + timedelta(days=180)  # 6 months
#             remaining_usages = 600  # Example value
        
#         # Update the Subscription model
#         subscription = Subscription(
#             plan=plan,
#             amount=amount,
#             start_date=start_date,
#             end_date=end_date,
#             remaining_usages=remaining_usages,
#             paid=True,
#             user_id=current_user.id,
#             paystack_subscription_id=paystack_subscription_id
#         )
#         db.session.add(subscription)
#         db.session.commit()
        
#         # Redirect to the dashboard
#         return redirect(url_for('dashboard'))
#     else:
#         # Optionally, redirect to an error page or return an error message
#         return redirect(url_for('error_page', error='Payment verification failed'))



# @core_bp.route('/payment_verification', methods=['GET', 'POST'])
# @login_required
# def payment_verification():
#     # Ensure the request has JSON content
#     if not request.is_json:
#         return jsonify({'error': 'Request must be JSON'}), 400

#     data = request.json
#     reference = data.get('reference')
#     if not reference:
#         return jsonify({'error': 'Reference not provided'}), 400

#     # URL to verify payment on Paystack
#     verification_url = f"https://api.paystack.co/transaction/verify/{reference}"
#     # Your Paystack secret key (use an environment variable in production)
#     secret_key = os.environ.get('PAYSTACK_SECRET_KEY')

#     try:
#         # Make a request to Paystack to verify the payment
#         headers = {"Authorization": secret_key, "Content-Type": "application/json"}
#         response = requests.get(verification_url, headers=headers)
#         response_data = response.json()

#         # Check if the request was successful and the payment is verified
#         if response.status_code == 200 and response_data['status'] == True and response_data['data']['status'] == 'success':
#             # Extract necessary information from the verification response
#             # Note: Adjust these according to the actual structure of Paystack's response
#             plan = response_data['data']['metadata']['plan']
#             amount = response_data['data']['amount']
#             paystack_subscription_id = response_data['data']['id']

#             # Calculate subscription dates based on plan
#             start_date = datetime.now()
#             if plan == 'Starter':
#                 end_date = start_date + timedelta(days=30)  # 1 month
#                 remaining_usages = 100  # Example value
#             elif plan == 'Basic':
#                 end_date = start_date + timedelta(days=90)  # 3 months
#                 remaining_usages = 300  # Example value
#             elif plan == 'Premium':
#                 end_date = start_date + timedelta(days=180)  # 6 months
#                 remaining_usages = 600  # Example value
            
#             # Update the Subscription model
#             subscription = Subscription(
#                 plan=plan,
#                 amount=amount / 100,  # Assuming amount is in cents
#                 start_date=start_date,
#                 end_date=end_date,
#                 remaining_usages=remaining_usages,
#                 paid=True,
#                 user_id=current_user.id,
#                 paystack_subscription_id=paystack_subscription_id
#             )
#             db.session.add(subscription)
#             db.session.commit()
            
#             # Redirect to the dashboard
#             return redirect(url_for('dashboard'))
#         else:
#             # Payment verification failed
#             return jsonify({'error': 'Payment verification failed'}), 400
#     except requests.RequestException as e:
#         # Handle request errors
#         return jsonify({'error': 'Failed to connect to Paystack'}), 500



# @core_bp.route('/payment_verify', methods=['GET', 'POST'])
# def verify_payment():
#     # Paystack sends a JSON payload to the webhook URL
#     data = request.json

#     # Extract the reference from the data
#     reference = data.get('data', {}).get('reference')

#     if not reference:
#         return jsonify({'message': 'No reference provided'}), 400

#     # Verify the payment by making a request to Paystack API
#     # This part is pseudo-code, adjust according to your Paystack integration library
#     verification_response = Transaction.verify(reference)

#     # Check if the payment is successful
#     if verification_response['data']['status'] == 'success':
#         # Find the subscription by reference
#         subscription = Subscription.query.filter_by(paystack_subscription_id=reference).first()
#         if subscription:
#             # Assuming you have a way to determine the plan details from the subscription instance or elsewhere
#             plans = {
#                 'Starter': {
#                     'cost': 2000,
#                     'duration': 1,  # number of days for the plan
#                     'usage_limit': 2,  # some usage limit
#                     # ... other plan details
#                 },
#                 'Basic': {
#                     'cost': 5000,
#                     'duration': 7,
#                     'usage_limit': 4,
#                     # ... other plan details
#                 },
#                 'Premium': {
#                     'cost': 10000,
#                     'duration': 30,
#                     'usage_limit': None,
#                     # ... other plan details
#                 }
#             }
#             plan_details = plans.get(subscription.plan)

#             # Update subscription status and details
#             subscription.paid = True
#             subscription.amount='cost'
#             subscription.start_date = datetime.utcnow()
#             subscription.end_date = datetime.utcnow() + timedelta(days=plan_details['duration'])
#             subscription.remaining_usages = plan_details['usage_limit']
            
#             db.session.commit()

#             return redirect(url_for('core.dashboard'))
        
#             return jsonify({'message': 'Payment verified and subscription updated'}), 200
#         else:
#             return jsonify({'message': 'Subscription not found'}), 404
#     else:
#         return jsonify({'message': 'Payment verification failed'}), 400

######
# @core_bp.route('/verify_payment', methods=['GET', 'POST'])
# @login_required
# def verify_payment():
#     paramz = request.args.get('trxref', 'None')

#     details = Transaction.verify(reference=paramz)
#     status = details['data']['status']

#     if status == 'success':
#         # Fetch or create the Subscription instance
#         subscription = Subscription.query.filter_by(paystack_subscription_id=paramz).first()

#         if subscription is None:
#             # Assume function `extract_plan_and_amount` returns plan name and amount
#             plan, amount = extract_plan_and_amount(details)

#             # Calculate end_date based on plan
#             if plan == 'Starter':
#                 end_date = datetime.utcnow() + timedelta(days=1)
#             elif plan == 'Basic':
#                 end_date = datetime.utcnow() + timedelta(days=7)
#             elif plan == 'Premium':
#                 end_date = datetime.utcnow() + timedelta(days=30)
#             else:
#                 return 'Invalid plan', 400

#             # Create a new subscription instance
#             subscription = Subscription(
#                 plan=plan,
#                 amount=amount,
#                 start_date=datetime.utcnow(),
#                 end_date=end_date,
#                 remaining_usages=plans[plan]['usage_limit'],
#                 paid=True,
#                 user_id=current_user.id,
#                 paystack_subscription_id=paramz
#             )
#             db.session.add(subscription)
#         else:
#             # Update existing subscription
#             subscription.paid = True
#             # Assuming `update_end_date` function updates the end_date based on the plan
#             subscription.end_date = update_end_date(subscription.plan, subscription.start_date)

#         # Update user subscription details
#         current_user.subscribed = True
#         current_user.expiry_date = subscription.end_date

#         db.session.commit()
#         print('Payment successful!')
#     else:
#         print('Payment not successful')

#     return redirect(url_for('core.dashboard'))

####

############
# @core_bp.route('/verify_payment', methods=['GET', 'POST'])
# @login_required
# def verify_payment():
#     paramz = request.args.get('trxref', 'None')

#     details = Transaction.verify(reference=paramz)
#     status = details['data']['status']

#     if status == 'success':
#         # Fetch or create the Subscription instance
#         subscription = Subscription.query.filter_by(paystack_subscription_id=paramz).first()

#         if subscription is None:
#             # Assume function `extract_plan_and_amount` returns plan name and amount
#             plan, amount = extract_plan_and_amount(details)

#             # Calculate end_date based on plan
#             if plan == 'Starter':
#                 end_date = datetime.utcnow() + timedelta(days=1)
#             elif plan == 'Basic':
#                 end_date = datetime.utcnow() + timedelta(days=7)
#             elif plan == 'Premium':
#                 end_date = datetime.utcnow() + timedelta(days=30)
#             else:
#                 return 'Invalid plan', 400

#             # Create a new subscription instance
#             subscription = Subscription(
#                 plan=plan,
#                 amount=amount,
#                 start_date=datetime.utcnow(),
#                 end_date=end_date,
#                 remaining_usages=plans[plan]['usage_limit'],
#                 paid=True,
#                 user_id=current_user.id,
#                 paystack_subscription_id=paramz
#             )
#             db.session.add(subscription)
#         else:
#             # Update existing subscription
#             subscription.paid = True
#             # Assuming `update_end_date` function updates the end_date based on the plan
#             subscription.end_date = update_end_date(subscription.plan, subscription.start_date)

#         # Update user subscription details
#         current_user.subscribed = True
#         current_user.expiry_date = subscription.end_date

#         db.session.commit()
#         print('Payment successful!')
#     else:
#         print('Payment not successful')

#     return redirect(url_for('core.dashboard'))

#############

def extract_plan_and_amount(details):
    """
    Extract the plan and amount from the payment details.
    Implement this based on how you're storing this information in the transaction details.
    """
    # Dummy implementation, replace with actual logic
    plan = details['data'].get('plan')
    amount = details['data'].get('amount')
    return plan, amount

def update_end_date(plan, start_date):
    """
    Calculate the end date based on the subscription plan.
    """
    if plan == 'Starter':
        return start_date + timedelta(days=1)
    elif plan == 'Basic':
        return start_date + timedelta(days=7)
    elif plan == 'Premium':
        return start_date + timedelta(days=30)
    else:
        return start_date



@core_bp.route('/tutor_fee_payment', methods=['GET', 'POST'])
@login_required
def tutor_fee_payment():
    amount = 10000  # use an integer for amount
    email = current_user.email
    tutor_id = current_user.id

    response = Transaction.initialize(amount=str(amount), email=email)  # convert amount to string here
    ref = response['data']['reference']
    print(f"{amount} {email} {tutor_id}")

    # Redirect to the payment authorization URL
    a_url = response['data']['authorization_url']
    return redirect(a_url)


# @core_bp.route('/verify_payment', methods=['GET', 'POST'])
# @login_required
# def verify_payment():
#     paramz = request.args.get('trxref', 'None')

#     details = Transaction.verify(reference=paramz)
#     status = details['data']['status']

#     if status == 'success':
#         # Find the subscription instance
#         pay_instance = Subscription.query.filter_by(paystack_subscription_id=paramz).first()
#         if pay_instance:
#             pay_instance.paid = True
#             expiry_date = datetime.utcnow()  # Default expiry date
#             if pay_instance.plan == 'Starter':
#                 expiry_date += timedelta(days=1)
#             elif pay_instance.plan == 'Basic':
#                 expiry_date += timedelta(days=7)
#             elif pay_instance.plan == 'Premium':
#                 expiry_date += timedelta(days=30)

#             pay_instance.end_date = expiry_date

#             # Update user subscription details
#             current_user.subscribed = True
#             current_user.expiry_date = expiry_date

#             # Create or update TutorFeePayment instance
#             tutor_fee_payment = TutorFeePayment.query.filter_by(transaction_id=paramz).first()
#             if not tutor_fee_payment:
#                 tutor_fee_payment = TutorFeePayment(
#                     transaction_id=paramz,
#                     amount=pay_instance.amount,
#                     paid_on=datetime.utcnow(),
#                     tutor_id=current_user.id  # or however you identify the tutor
#                 )
#                 db.session.add(tutor_fee_payment)
#             else:
#                 tutor_fee_payment.amount = pay_instance.amount
#                 tutor_fee_payment.paid_on = datetime.utcnow()

#             # Associate the payment with the tutor
#             current_user.fee_payments.append(tutor_fee_payment)

#             db.session.commit()
#             print('Payment successful!')
#         else:
#             print('Subscription not found for the given transaction reference.')
#     else:
#         print('Payment not successful')

#     return redirect('core.dashboard')




















# @core_bp.route('/subscribe_starter', methods=['GET', 'POST'])
# @login_required
# def subscribe_starter():
#     plan = 'Starter'
#     amount = '20000'
#     first_name = current_user.first_name
#     last_name = current_user.last_name
#     email = current_user.email

#     response = Transaction.initialize(amount=amount, email=email)

#     ref = response.get('data', {}).get('reference')
#     print(f"{first_name} {last_name}")
    
#     create_subscription_instance = Subscription(
#         plan='Starter',
#         amount=2000,
#         start_date=datetime.utcnow(),
#         end_date=datetime.utcnow() + timedelta(days=plans['starter']['duration']),
#         remaining_usages=plans['starter']['usage_limit'],
#         paid=True,
#         user_id=current_user.id,
#         paystack_subscription_id=response.get('data', {}).get('reference')
#     )

#     db.session.add(create_subscription_instance)
#     db.session.commit()

#     a_url = response['data']['authorization_url']
#     return redirect(a_url)


# @core_bp.route('/subscribe_basic', methods=['GET', 'POST'])
# @login_required
# def subscribe_basic():
#     amount = '5000'
#     first_name = current_user.first_name
#     last_name = current_user.last_name
#     email = current_user.email

#     response = Transaction.initialize(amount=amount, email=email)

#     ref = response['data']['reference']
#     print(f"{first_name} {last_name}")
    
#     create_subscription_instance = Subscription(
#         plan='Starter',
#         amount=5000,
#         start_date=datetime.utcnow(),
#         end_date=datetime.utcnow() + timedelta(days=plans['basic']['duration']),
#         remaining_usages=plans['basic']['usage_limit'],
#         paid=True,
#         user_id=current_user.id,
#         paystack_subscription_id=response['data']['reference']
#     )
#     db.session.add(create_subscription_instance)
#     db.session.commit()

#     a_url = response['data']['authorization_url']
#     return redirect(a_url)


# @core_bp.route('/subscribe_premium', methods=['GET', 'POST'])
# @login_required
# def subscribe_premium():
#     amount = '10000'
#     first_name = current_user.first_name
#     last_name = current_user.last_name
#     email = current_user.email

#     response = Transaction.initialize(amount=amount, email=email)

#     ref = response['data']['reference']
#     print(f"{first_name} {last_name}")
    
#     create_subscription_instance = Subscription(
#         plan='Starter',
#         amount=10000,
#         start_date=datetime.utcnow(),
#         end_date=datetime.utcnow() + timedelta(days=plans['premium']['duration']),
#         remaining_usages=plans['premium']['usage_limit'],
#         paid=True,
#         user_id=current_user.id,
#         paystack_subscription_id=response['data']['reference']
#     )
#     db.session.add(create_subscription_instance)
#     db.session.commit()

#     a_url = response['data']['authorization_url']
#     return redirect(a_url)


@core_bp.route('/verify_payment', methods=['GET', 'POST'])
@login_required
def verify_payment():
    paramz = request.args.get('trxref', 'None')
    first_name = current_user.first_name
    last_name = current_user.last_name
    email = current_user.email
    print(paramz)
    
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

            """Update the user subscription details"""
            current_user.update(subscribed=True, expiry_date=expiry_date)
            print('Payment successful!')
        else:
            print('Subscription not found for the given transaction reference.')

    else:
        print('Payment not successful')

    return redirect('core.dashboard')


# Tutor registration fee
fees = {
    'registration_fee': {'name': 'Registration Fee', 'cost': 10000}
}

# @core_bp.route('/tutor_fee_payment', methods=['GET', 'POST'])
# @login_required
# def tutor_fee_payment():
#     amount = '10000'
#     email = current_user.email
#     tutor_id = current_user.id

#     response = Transaction.initialize(amount=amount, email=email)

#     ref = response['data']['reference']
#     print(f"{amount} {email} {tutor_id}")

#     tutor = Tutor.query.get(tutor_id)

#     if tutor:
#         tutor_fee_payment_instance = TutorFeePayment(
#             tutor_id=tutor_id,
#             amount=10000,
#             payment_date=datetime.now()
#         )

#         db.session.add(tutor_fee_payment_instance)
#         db.session.commit()

#     a_url = response['data']['authorization_url']
#     return redirect(a_url)
#     return render_template('core/tutor_fee_payment.html', amount=amount, ref=ref, email=email)






@core_bp.route('/service_fee_payment', methods=['GET', 'POST'])
@login_required
def service_fee_payment():
    return render_template('core/tutor_fee_payment.html', fees=fees)


######################################
#   Tutors Registration routes       #
######################################

# Tutor registration form
@core_bp.route('/tutor_registration', methods=['GET', 'POST'])
def tutor_registration():
    """
    Handle file upload
    """
    if 'photo' in request.files:
        photo = request.files['photo']

        """Check if the file is selected"""
        if photo.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        """
        Check if the file is allowed
        """
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if '.' in photo.filename and photo.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            flash('Invalid file type. Allowed types are png, jpg, jpeg, gif', 'error')
            return redirect(request.url)
        
    return render_template('core/tutor_registration_form.html')


# Tutor registration route to process the form
@core_bp.route('/process-registration', methods=['POST'])
def process_registration():
    try:
        # Retrieve form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        address = request.form['address']
        phone_number = request.form['phone_number']
        age = request.form['age']
        education_qualification = request.form['education_qualification']
        interest = request.form['interest']
        subjects = request.form['subjects']
        past_experience = 'past_experience' in request.form
        experience_years = request.form['experience_years']
        experience_description = request.form['experience_description']
        interest_join = request.form['interest_join']
        languages = request.form['languages']
        availability = request.form['availability']
        teaching_mode = request.form['teaching_mode']
        student_level = request.form['student_level']
        source = request.form['source']
        confirmation_name = request.form['confirmation_name']
        photo = request.files['photo']

        # Create a new Tutor instance
        tutor = Tutor(
            id=None,
            first_name=first_name,
            last_name=last_name,
            email=email,
            address=address,
            phone_number=phone_number,
            age=age,
            education_qualification=education_qualification,
            interest=interest,
            subjects=subjects,
            past_experience=past_experience,
            experience_years=experience_years,
            experience_description=experience_description,
            interest_join=interest_join,
            languages=languages,
            availability=availability,
            teaching_mode=teaching_mode,
            student_level=student_level,
            source=source,
            confirmation_name=confirmation_name,
            photo_data=photo.read(),
            photo_filename=secure_filename(photo.filename),
            user_id=current_user.id 
        )

        # Add the new tutor to the database
        db.session.add(tutor)
        db.session.commit()

        flash('Registration successful!', 'success')
        return render_template('core/tutor_fee_payment.html', fees=fees)

    except Exception as e:
        # Rollback the transaction in case of an error
        db.session.rollback()
        # Flash error message
        flash('Registration failed. Please try again.', 'error')
        print(f'Error: {str(e)}')
        return redirect(url_for('core.tutor_registration'))


@core_bp.route('/register_parent', methods=['GET', 'POST'])
@login_required
def register_parent():
    form = ParentRegistrationForm()

    if form.validate_on_submit():
        # Check if the email is already registered
        existing_parent = Parent.query.filter_by(email=form.email.data).first()

        if existing_parent:
            flash('This email is already registered. Please use a different email address.', 'danger')
        else:
            try:
                parent = Parent(
                    full_name=form.full_name.data,
                    phone_number=form.phone_number.data,
                    email=form.email.data,
                    age_range=form.age_range.data,
                    subject_area=form.subject_area.data,
                    user_id=current_user.id
                )

                db.session.add(parent)
                db.session.commit()

                flash('Registration successful!', 'success')
                return redirect(url_for('core.tutor_exploration'))

            except Exception as e:
                # Handle unexpected errors, log the error, and display a flash message
                db.session.rollback()
                flash('An unexpected error occurred. Please try again later.', 'danger')
                print(f"Error during registration: {e}")
    return render_template('accounts/register_parent.html', form=form, errors=form.errors)


@core_bp.route('/tutor_profile/<int:tutor_id>')
@login_required
def tutor_profile(tutor_id):
    tutor = Tutor.query.get_or_404(tutor_id)
    return render_template('accounts/tutor_profile.html', tutor=tutor)


# Add this route to your Flask application
@core_bp.route('/search_tutors', methods=['GET', 'POST'])
@login_required
@check_is_registered
def search_tutors():
    if request.method == 'POST':
        subject_to_search = request.form.get('subject')
        tutors = Tutor.query.filter(Tutor.subjects.ilike(f'%{subject_to_search}%')).all()
    else:
        tutors = Tutor.query.all()

    return render_template('accounts/search_tutors.html', tutors=tutors)


@core_bp.route('/registered_parents')
def registered_parents():
    # Query your database for all registered parents
    parents = Parent.query.all()  # Replace with your actual database query

    # Render a template, passing the parents data
    return render_template('accounts/registered_parents.html', parents=parents)


@core_bp.route('/registered_tutors')
def registered_tutors():
    # Query your database for all registered tutors
    tutors = Tutor.query.all()  # Replace with your actual database query

    # Render a template, passing the tutors data
    return render_template('accounts/tutors_list.html', users=[tutor.user for tutor in tutors])


from flask import send_file

@core_bp.route('/accounts/display_photo/<int:tutor_id>')
def display_photo(tutor_id):
    tutor = Tutor.query.get(tutor_id)
    if tutor and tutor.photo_path:
        return send_file(tutor.photo_path, mimetype='image/jpeg')
    else:
        return send_file('path_to_default_image', mimetype='image/jpeg')


# @core_bp.route('/subscribed_users')
# def subscribed_users():
#     users = User.query.filter(User.subscription.isnot(None)).all()
#     return render_template('accounts/subscribed_users.html', users=users)


@core_bp.route('/subscribed_users')
def subscribed_users():
    users = User.query.filter(User.subscription != None).all()
    return render_template('accounts/subscribed_users.html', users=users)
    



@core_bp.route('/delete_subscribed_user/<int:subscription_id>')
@login_required  
def delete_subscribed_user(subscription_id):
    subscription_to_delete = Subscription.query.get(subscription_id)
    if subscription_to_delete:
        db.session.delete(subscription_to_delete)
        db.session.commit()
        flash('Subscription successfully removed', 'success')
    else:
        flash('Subscription not found', 'error')
    return redirect(url_for('core.subscribed_users'))


# @core_bp.route('/subscribe_starter', methods=['GET', 'POST'])
# @login_required
# def subscribe_starter():
#     plan = 'Starter'
#     amount = '20000'
#     email = current_user.email

#     response = Transaction.initialize(amount=amount, email=email)
#     ref = response.get('data', {}).get('reference')

#     a_url = response['data']['authorization_url']
#     return redirect(a_url)


# @core_bp.route('/subscribe_basic', methods=['GET', 'POST'])
# @login_required
# def subscribe_basic():
#     plan = 'Basic'
#     amount = '5000'
#     email = current_user.email

#     response = Transaction.initialize(amount=amount, email=email)
#     ref = response['data']['reference']

#     a_url = response['data']['authorization_url']
#     return redirect(a_url)


# @core_bp.route('/subscribe_premium', methods=['GET', 'POST'])
# @login_required
# def subscribe_premium():
#     plan = 'Premium'
#     amount = '10000'
#     email = current_user.email

#     response = Transaction.initialize(amount=amount, email=email)
#     ref = response['data']['reference']
#     print(ref)

#     a_url = response['data']['authorization_url']
#     print(a_url)
#     return redirect(a_url)


# @core_bp.route('/verify_payment', methods=['POST'])
# @login_required
# def verify_payment():
#     data = request.json
#     ref = data.get('reference')
#     if not ref:
#         return jsonify({"message": "Payment reference not provided"}), 400

#     """Verify payment with Paystack"""
#     paystack_secret_key = "PAYSTACK_SECRET_KEY"
#     verification_url = f"https://api.paystack.co/transaction/verify/{ref}"
#     headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
#     response = requests.get(verification_url, headers=headers)
#     verification_response = response.json()

#     if response.status_code != 200 or verification_response['data']['status'] != 'success':
#         return jsonify({"message": "Payment verification failed"}), 400

#     amount = verification_response['data']['amount']
#     paystack_subscription_id = verification_response['data']['subscription']['subscription_code']
    
#     if amount == 20000:
#         plan = 'Starter'
#     elif amount == 5000:
#         plan = 'Basic'
#     elif amount == 10000:
#         plan = 'Premium'
#     else:
#         return jsonify({"message": "Invalid payment amount"}), 400


#     start_date, end_date, remaining_usages = calculate_subscription_dates_and_usages(plan)

#     # Update or create subscription in thegit database
#     subscription = Subscription.query.filter_by(user_id=current_user.id, plan=plan).first()
#     if subscription:
#         # Update existing subscription
#         # subscription.update(amount = amount, start_date = start_date, end_date = end_date, remaining_usages = remaining_usages, paid = True, paystack_subscription_id = paystack_subscription_id)
        
#         subscription.amount = amount
#         subscription.start_date = start_date
#         subscription.end_date = end_date
#         subscription.remaining_usages = remaining_usages
#         subscription.paid = True
#         subscription.paystack_subscription_id = paystack_subscription_id
#     else:
#         subscription = Subscription(user_id=current_user.id, plan=plan, amount=amount,
#                                     start_date=start_date, end_date=end_date, remaining_usages=remaining_usages,
#                                     paid=True, paystack_subscription_id=paystack_subscription_id)
#         db.session.add(subscription)

#     db.session.commit()
#     return redirect(url_for('core.dashboard'))


def calculate_subscription_dates_and_usages(plan):
    """Current time as the start date"""
    start_date = datetime.utcnow()
    end_date = start_date + timedelta(days=30)

    if plan == 'Starter':
        remaining_usages = 10
    elif plan == 'Basic':
        remaining_usages = 20
    elif plan == 'Premium':
        remaining_usages = 40
    else:
        remaining_usages = 20

    return start_date, end_date, remaining_usages





def extract_plan_and_amount(details):
    """
    Extract the plan and amount from the payment details.
    Implement this based on how you're storing this information in the transaction details.
    """
    plan = details['data'].get('plan')
    amount = details['data'].get('amount')
    return plan, amount

def update_end_date(plan, start_date):
    """
    Calculate the end date based on the subscription plan.
    """
    if plan == 'Starter':
        return start_date + timedelta(days=1)
    elif plan == 'Basic':
        return start_date + timedelta(days=7)
    elif plan == 'Premium':
        return start_date + timedelta(days=30)
    else:
        return start_date





# @core_bp.route('/paystack/webhook', methods=['GET', 'POST'])
# def paystack_webhook():
#     data = request.json

#     if data['event'] == 'charge.success':
#         reference = data['data']['reference']
#         subscription = Subscription.query.filter_by(paystack_subscription_id=reference).first()
#         if subscription:
#             subscription.paid = True
#             db.session.commit()
#             return jsonify({"status": "success"}), 200
#         return redirect(url_for('core.dashboard'))
#     return jsonify({"status": "error"}), 400




# 1
# @core_bp.route('/payment_verification', methods=['POST'])
# def payment_verification():
#     data = request.json

#     reference = data.get('reference')
#     success = data.get('status') == 'success'

#     if success:
#         # Update subscription status in the database
#         subscription = Subscription.query.filter_by(paystack_subscription_id=reference).first()
#         if subscription:
#             subscription.paid = True
#             db.session.commit()

#             return jsonify({'message': 'Payment verified successfully'}), 200
#     return jsonify({'message': 'Payment verification failed'}), 400


#2
# @core_bp.route('/payment_verification', methods=['POST'])
# def payment_verification():
#     data = request.json
#     paramz = request.GET.get('trxref', 'None')
#     print(paramz)

#     reference = data.get('reference')
#     # success = data.get('status') == 'success'

#     status = details['data']['status']

#     details = Transaction.verify(reference=paramz)

#     if status == 'success':
#         # Update subscription status in the database
#         subscription = Subscription.query.filter_by(paystack_subscription_id=reference=paramz).first()
#         if subscription:
#             subscription.paid = True
#             db.session.commit()

#             # Redirect to core.dashboard
#             return redirect(url_for('core.dashboard'))  

#     # For failed verifications, still return JSON for consistency
#     return jsonify({'message': 'Payment verification failed'}), 400 


# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         # Implement your login check here
#         if not current_user.is_authenticated:
#             return redirect(url_for('login', next=request.url))
#         return f(*args, **kwargs)
#     return decorated_function