from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, TextAreaField, PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length, DataRequired, Email, Length
from src.accounts.models import User
from wtforms import SelectField, BooleanField, IntegerField
from wtforms.validators import Optional, InputRequired
from wtforms import DecimalField, DateField, IntegerField

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])


class RegisterForm(FlaskForm):
    email = StringField(
        "Email", validators=[DataRequired(), Email(), Length(min=6, max=40)]
    )
    first_name = StringField(
        "First Name", validators=[DataRequired(), Length(min=2, max=25)]
    )
    last_name = StringField(
        "Last Name", validators=[DataRequired(), Length(min=2, max=25)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6, max=25)]
    )
    confirm = PasswordField(
        "Repeat password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )

    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("Email already registered")
            return False
        if self.password.data != self.confirm.data:
            self.password.errors.append("Passwords must match")
            return False
        return True

class LessonPlanForm(FlaskForm):
    prompt = TextAreaField('Enter a topic or description', validators=[DataRequired()])
    submit = SubmitField('Generate Lesson Plan')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password',
                                     validators=[DataRequired(),
                                                 EqualTo('password')])
    submit = SubmitField('Reset Password')



class TutorRegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    address = StringField('Address', validators=[Length(max=200)])
    phone_number = StringField('Phone Number', validators=[Length(max=15)])
    age = IntegerField('Age', validators=[Optional()])
    education_qualification = SelectField('Highest Educational Qualification',
                                          choices=[('Diploma', 'Diploma'), ('Graduate', 'Graduate'),
                                                   ('Masters', 'Masters'), ('Doctorate', 'Doctorate'),
                                                   ('Others', 'Others')],
                                          validators=[Optional()])
    interest = TextAreaField('Why are you interested in being a tutor?', validators=[DataRequired()])
    subjects = StringField('Subjects', validators=[DataRequired(), Length(max=200)])
    past_experience = BooleanField('Do you have any past tutoring experience?')
    experience_years = SelectField('Years of Experience',
                                   choices=[('Less than 4 months', 'Less than 4 months'),
                                            ('4 months - 1 year', '4 months - 1 year'),
                                            ('1-3 years', '1-3 years'),
                                            ('3-5 years', '3-5 years'),
                                            ('More than 5 years', 'More than 5 years'),
                                            ('Others', 'Others')],
                                   validators=[Optional()])
    experience_description = TextAreaField('Tell us a few words about your experience', validators=[Optional()])
    interest_join = TextAreaField('What interests you to join us?', validators=[DataRequired()])
    languages = TextAreaField('List out the languages you know', validators=[DataRequired()])
    availability = SelectField('Days Available for Tutoring',
                               choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
                                        ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'),
                                        ('Sunday', 'Sunday')],
                               validators=[Optional()])
    teaching_mode = SelectField('Preferred Mode of Teaching',
                                choices=[('Online class', 'Online class'), ('Physical Classroom', 'Physical Classroom')],
                                validators=[Optional()])
    student_level = SelectField('Level of Students You Would Like to Teach',
                                choices=[('Primary', 'Primary'), ('Secondary', 'Secondary'), ('Undergraduate', 'Undergraduate')],
                                validators=[Optional()])
    source = SelectField('Where did you hear about us',
                         choices=[('Newspaper', 'Newspaper'), ('Family/friend', 'Family/friend'),
                                  ('Social media', 'Social media'), ('Others', 'Others')],
                         validators=[Optional()])
    confirmation_name = StringField('Applicant Name (as a signature to confirm your application)',
                                   validators=[DataRequired(), Length(max=10)])
    
    submit = SubmitField('Submit')

class TutorFeePaymentForm(FlaskForm):
    tutor_id = IntegerField('Tutor ID', validators=[InputRequired()])
    amount = DecimalField('Amount', validators=[InputRequired()])
    payment_date = DateField('Payment Date', validators=[InputRequired()])