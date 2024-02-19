from datetime import datetime, timedelta
# from your_app import db  # Assuming you have your database setup
# from your_app.models import Subscription  # Import the Subscription model
from src.accounts.models import Subscription, db

def subscribe_user(user_id, paystack_subscription_id, plan, amount, end_date=None, remaining_usages=None):
    """Manually subscribes a user to a plan.

    Args:
        user_id (int): The ID of the user to subscribe.
        plan (str): The name of the subscription plan.
        end_date (datetime, optional): The end date of the subscription.
            Defaults to None, indicating no end date.
        remaining_usages (int, optional): The number of remaining usages for the plan.
            Defaults to None, indicating unlimited usages.
    """

    if end_date is None:
        end_date = datetime.utcnow() + timedelta(days=365)  # Set end date to 1 year from now

    subscription = Subscription(user_id=user_id, plan=plan, amount=amount, end_date=end_date, remaining_usages=remaining_usages)
    db.session.add(subscription)
    db.session.commit()

    print(f"User {user_id} successfully subscribed to plan {plan}.")

# Example usage:
subscribe_user(user_id=7, paystack_subscription_id=232, plan="Premium", amount=5000, end_date=datetime(2024, 1, 31), remaining_usages=100)
