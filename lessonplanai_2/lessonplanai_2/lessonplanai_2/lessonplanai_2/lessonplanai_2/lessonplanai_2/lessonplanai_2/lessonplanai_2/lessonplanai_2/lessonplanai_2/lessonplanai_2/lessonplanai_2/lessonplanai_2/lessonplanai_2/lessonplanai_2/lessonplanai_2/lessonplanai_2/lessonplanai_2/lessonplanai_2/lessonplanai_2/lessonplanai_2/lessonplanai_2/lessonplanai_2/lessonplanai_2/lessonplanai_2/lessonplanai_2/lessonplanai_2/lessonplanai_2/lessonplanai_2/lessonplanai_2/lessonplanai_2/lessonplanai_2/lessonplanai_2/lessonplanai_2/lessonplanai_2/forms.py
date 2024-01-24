from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms import StringField, PasswordField, SubmitField, IntegerField, RadioField
from wtforms.validators import DataRequired, Email, Length


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    sex = RadioField('Sex', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    profession = StringField('Profession', validators=[DataRequired()])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class LessonPlanForm(FlaskForm):
    prompt = TextAreaField('Enter a topic or description', validators=[DataRequired()])
    submit = SubmitField('Generate Lesson Plan')

# Define the ContactForm class here
class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])


