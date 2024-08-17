from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin
from sqlalchemy import CheckConstraint , UniqueConstraint
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, ForeignKey, Boolean, Float, ForeignKeyConstraint, Table
from sqlalchemy.orm import relationship, declarative_base
#from flask_debugtoolbar import  DebugToolbarExtension


app = Flask(__name__)
#app.debug = True
app.config['SECRET_KEY'] = '275159fcd3bf7264d16dd63a3e300d15'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/site'
#toolbar = DebugToolbarExtension(app)

db = SQLAlchemy(app)
migrate = Migrate(app,db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

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

    employee_id = Column(Integer, ForeignKey('employee.id'), nullable=True)
    # Relationships
    employee = relationship("Employee", uselist=False, back_populates="user")

    def __repr__(self):
        return f"User('{self.username}',{self.email}','{self.employee_id}','{self.firstname},'{self.lastname})"

employee_service = Table('employee_service', db.Model.metadata,
    Column('employee_id', Integer, ForeignKey('employee.id')),
    Column('service_id', Integer, ForeignKey('services.service_id'))
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
    username = db.Column(db.String(100), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)

    employee = db.relationship('Employee', backref=db.backref('appointments', lazy=True))
    service = db.relationship('Service')


from salonManagement import routes #to avoid circular import 