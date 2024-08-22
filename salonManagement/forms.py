from os import walk
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, RadioField, SubmitField, BooleanField, TextAreaField, validators
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from salonManagement import User,bcrypt,Employee

class SignUpForm(FlaskForm):
    usertype = RadioField('User Type', choices=[('user', 'User'), ('employee', 'Employee')], default='user')
    empid = StringField('Employee ID', [validators.Optional()])  
    username = StringField('Username', [validators.DataRequired()])
    email = StringField('Email', [validators.Email(), validators.DataRequired()])
    pwd = PasswordField('Password', [validators.DataRequired()])
    confirm_pwd = PasswordField('Re-type Password', [validators.EqualTo('pwd', message='Passwords must match')])
    submit = SubmitField('Sign up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'That username is taken. Please choose a different one')
        
    def validate_employee(self, empid):
      
        if self.usertype.data != 'employee':
            return

        if empid.data:
            employee = User.query.filter_by(username=empid.data).first()
            if employee:
                raise ValidationError('That employee ID is taken. Please choose a different one')

            if not Employee.query.filter_by(id=empid.data).first():
                raise ValidationError('Invalid employee ID')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                'That email is taken. Please choose a different one')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is None:
            raise ValidationError("No account found with this username.")
    
    def validate_password(self, password):
        user = User.query.filter_by(username=self.username.data).first()
        if user and not bcrypt.check_password_hash(user.password, password.data):
            raise ValidationError("Incorrect password.")