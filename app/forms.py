from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, \
    HiddenField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length, \
    NumberRange, Optional
from wtforms.widgets import HiddenInput
from app.models import User, Employee


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], default='')
    password = PasswordField('Password', validators=[DataRequired()], default='')
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField(
        'Username', validators=[DataRequired(), Length(max=User.USERNAME_MAX_LEN)], default='')
    email = StringField('E-mail', validators=[DataRequired(), Email()], default='')
    password = PasswordField('Password', validators=[DataRequired()], default='')
    password_repeat = PasswordField(
        'Repeat Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')],
        default='')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('This username is already taken.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('This email address is already taken.')

class EmployeeForm(FlaskForm):
    id = IntegerField('ID', widget=HiddenInput(), validators=[NumberRange(min=1), Optional()])
    full_name = StringField('Full name', validators=[DataRequired()])
    position = StringField('Position', validators=[DataRequired()])
    hire_date = DateField('Hire date', validators=[DataRequired()])
    salary = IntegerField('Salary', validators=[DataRequired(), NumberRange(min=0)])
    supervisor_id = IntegerField('Supervisor ID', validators=[NumberRange(min=1), Optional()])
    submit = SubmitField('Submit')

    def validate_supervisor_id(self, supervisor_id):
        try:
            id = int(supervisor_id.data)
        except ValueError:
            pass
        if not Employee.query.get(id):
            raise ValidationError('Employee with such ID doesn\'t exist!')


class EmployeeDeleteForm(FlaskForm):
    id = IntegerField('ID', widget=HiddenInput(), validators=[NumberRange(min=1)])
    replacement_id = IntegerField(
        'Replacement ID (optional)',
        validators=[NumberRange(min=1), Optional()],
        default='',
        description='All direct subordinates will be transferred to this employee')
    submit = SubmitField('Submit')

    def validate_replacement_id(self, replacement_id):
        try:
            id = int(replacement_id.data)
        except ValueError:
            pass
        if not Employee.query.get(id):
            raise ValidationError('Employee with such ID doesn\'t exist!')
