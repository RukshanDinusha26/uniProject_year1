from flask import Flask
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin
from sqlalchemy import CheckConstraint , UniqueConstraint
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, ForeignKey, Boolean, Float, ForeignKeyConstraint, Table, PrimaryKeyConstraint
from sqlalchemy.orm import relationship, declarative_base
from dotenv import load_dotenv
import os
#from flask_debugtoolbar import  DebugToolbarExtension
load_dotenv()

app = Flask(__name__)
#app.debug = True
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51PqF5s03J51F01u1MJyZV1r4leN0RdCIKiDznE7QVjk5DJffNOqyBP5H3K1bBzB9YXus91uQtkMBMUPHrCZYXWlx00edtGCRiQ'
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51PqF5s03J51F01u1UzTInMrSWuZXKUGvF9knMyC6Ks9MVEQvqfBlYdyOPtTuWDQAj05zXFX5OZQYFEfhQ0ky54tB00WYbRjW9S'
#toolbar = DebugToolbarExtension(app)
UPLOAD_FOLDER = 'salonManagement/static/uploads/'
REPORT_FOLDER = 'salonManagement/static/reports/appointment_report.csv'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORT_FOLDER'] = REPORT_FOLDER
PROFILE_UPLOAD_FOLDER = 'salonManagement/static/profile'
app.config['PROFILE_UPLOAD_FOLDER'] = PROFILE_UPLOAD_FOLDER
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

db = SQLAlchemy(app)
migrate = Migrate(app,db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'home'



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    firstname = Column(String(50))
    lastname = Column(String(50))
    about = Column(Text)
    age = Column(Integer)
    dob = Column(Date)
    address = Column(Text)
    gender = Column(String(10))
    profile_image = db.Column(db.String(255)) 
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    employee_id = Column(Integer, ForeignKey('employee.id'), nullable=True)
    # Relationships
    employee = relationship("Employee", uselist=False, back_populates="user",single_parent=True)

    def __repr__(self):
        return f"User('{self.username}',{self.email}','{self.employee_id}','{self.firstname},'{self.lastname})"

employee_service = Table(
    'employee_service', db.Model.metadata,
    Column('employee_id', Integer, ForeignKey('employee.id')),
    Column('service_id', Integer, ForeignKey('services.service_id')),
    PrimaryKeyConstraint('employee_id', 'service_id')
)
class Employee(db.Model):
    __tablename__ = 'employee'

    id = Column(Integer, primary_key=True)
    user = relationship('User', back_populates='employee', uselist=False)
    
    # Define the many-to-many relationship with the Service model
    services = relationship('Service', secondary=employee_service, back_populates='employees')

    def __repr__(self):
        return f"Employee('{self.id}')"

class Service(db.Model):
    __tablename__ = 'services'
    
    service_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    service_name = db.Column(db.String(100), nullable=False)
    service_image = db.Column(db.String(255))  # Stores image file path or URL
    price = db.Column(db.Float, nullable=False)

    # Define the many-to-many relationship with the Employee model
    employees = relationship('Employee', secondary=employee_service, back_populates='services')

    def __repr__(self):
        return f"Service('{self.service_name}','{self.service_id}','{self.service_image}','{self.price}')"

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token_number = db.Column(db.String(12), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    payment_status = db.Column(db.String(20), nullable=False, default='Pending')
    status = db.Column(db.String(20), nullable=False, default='Pending')

    employee = db.relationship('Employee', backref=db.backref('appointments', lazy=True))
    service = db.relationship('Service')


from salonManagement import routes #to avoid circular import 