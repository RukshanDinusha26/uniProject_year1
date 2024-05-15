from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin
from sqlalchemy import CheckConstraint
#from flask_debugtoolbar import  DebugToolbarExtension


app = Flask(__name__)
#app.debug = True
app.config['SECRET_KEY'] = '275159fcd3bf7264d16dd63a3e300d15'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
#toolbar = DebugToolbarExtension(app)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    accType = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    fname=db.Column(db.String(120))
    lname=db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    employee_id = db.Column(db.String(20),db.ForeignKey('employee.employee_id'), nullable=True, server_default=None)

    employee = db.relationship('Employee', back_populates='user')
    appointment = db.relationship('Appointment', back_populates='user')

    def __repr__(self):
        return f"User('{self.accType}','{self.username}',{self.email}','{self.password}','{self.employee_id}')"

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),db.ForeignKey('user.username'),nullable=False) 
    employee_name = db.Column(db.String(255),nullable=False)
    employee_id = db.Column(db.String(255), db.ForeignKey('employee.employee_id'),nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False, unique = True)

    user = db.relationship('User', back_populates='appointment')
    employee = db.relationship('Employee', back_populates='appointment')

    def __repr__(self):
        return f"Appointment('{self.username}','{self.employee_name}',{self.employee_id}','{self.date}',{self.time}')"

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), nullable=False, unique=True)
    employee_name = db.Column(db.String(255))
    employee_type = db.Column(db.String(255))

    user = db.relationship('User', back_populates='employee')
    appointment = db.relationship('Appointment', back_populates='employee')

    

from salonManagement import routes #to avoid circular import 