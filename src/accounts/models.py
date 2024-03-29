from datetime import datetime

from flask_login import UserMixin

from src import bcrypt, db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_confirmed = db.Column(db.Boolean, nullable=True, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

    # Add the relationship to Subscription
    subscription = db.relationship('Subscription', backref='user', uselist=False)
    tutor = db.relationship('Tutor', backref='user', uselist=False)

    def __init__(self, email, first_name, last_name, password, 
                 is_admin=False, is_confirmed=False, confirmed_on=None):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password = bcrypt.generate_password_hash(password)
        self.created_on = datetime.now()
        self.is_admin = is_admin
        self.is_confirmed = is_confirmed
        self.confirmed_on = confirmed_on

    def __repr__(self):
        return f"<User {self.email}>" 


class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    plan = db.Column(db.String(50))
    amount = db.Column(db.Integer)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    remaining_usages = db.Column(db.Integer)
    paid = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    paystack_subscription_id = db.Column(db.String(50), nullable=False)

    def __init__(self, plan, amount, start_date, end_date, remaining_usages, paid, paystack_subscription_id, user_id):
        self.plan = plan
        self.amount = amount
        self.start_date = start_date
        self.end_date = end_date
        self.remaining_usages = remaining_usages
        self.paid = paid
        self.paystack_subscription_id = paystack_subscription_id
        self.user_id = user_id

    def __repr__(self):
        return f"<Subscription {self.plan} - User {self.user_id}>"


class Tutor(db.Model):
    __tablename__ = "tutor"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    address = db.Column(db.String(200))
    phone_number = db.Column(db.String(15))
    age = db.Column(db.Integer)
    education_qualification = db.Column(db.String(50))
    interest = db.Column(db.Text)
    subjects = db.Column(db.String(200))
    past_experience = db.Column(db.Boolean)
    experience_years = db.Column(db.String(20))
    experience_description = db.Column(db.Text)
    interest_join = db.Column(db.Text)
    languages = db.Column(db.Text)
    availability = db.Column(db.String(50))
    teaching_mode = db.Column(db.String(50))
    student_level = db.Column(db.String(50))
    source = db.Column(db.String(50))
    confirmation_name = db.Column(db.String(100))
    fee_paid = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # fee_payments = db.relationship('TutorFeePayment', back_populates='tutor')
    photo_data = db.Column(db.LargeBinary)
    photo_filename = db.Column(db.String(255))
   
    


    def __init__(self, id, first_name, last_name, email, address, phone_number, age, education_qualification,
                 interest, subjects, past_experience, experience_years, experience_description, interest_join, 
                 languages, availability, teaching_mode, student_level, source, confirmation_name, user_id, photo_data=None, photo_filename=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.address = address
        self.phone_number = phone_number
        self.age = age
        self.education_qualification = education_qualification
        self.interest = interest
        self.subjects = subjects
        self.past_experience = past_experience
        self.experience_years = experience_years
        self.experience_description = experience_description
        self.interest_join = interest_join
        self.languages = languages
        self.availability = availability
        self.teaching_mode = teaching_mode
        self.student_level = student_level
        self.source = source
        self.confirmation_name = confirmation_name
        # self.fee_paid = fee_paid
        self.user_id = user_id
        self.photo_data = photo_data
        self.photo_filename = photo_filename

    def __repr__(self):
        return f"<Tutor {self.first_name} - User {self.user_id}>"


class TutorFeePayment(db.Model):
    __tablename__ = "tutorfeepayment"

    id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutor.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    paystack_tutorfeepayment_id = db.Column(db.String(50), nullable=False)
    # tutor = db.relationship('Tutor', back_populates='fee_payments')
    

    def __init__(self, tutor_id, amount, payment_date, paystack_tutorfeepayment_id):
        self.tutor_id = tutor_id
        self.amount = amount
        self.payment_date = payment_date
        self.paystack_tutorfeepayment_id = paystack_tutorfeepayment_id


class Parent(db.Model):
    __tablename__ = "parent"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    age_range = db.Column(db.String(20))
    subject_area = db.Column(db.String(100))
    state = db.Column(db.String(100))
    local_government = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('parent', lazy=True))

    def __init__(self, full_name, phone_number, email, age_range, subject_area, state, local_government, user_id):
        self.full_name = full_name
        self.phone_number = phone_number
        self.email = email
        self.age_range = age_range
        self.subject_area = subject_area
        self.state = state
        self.local_government = local_government
        self.user_id = user_id