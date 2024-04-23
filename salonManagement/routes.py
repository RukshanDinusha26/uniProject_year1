import json
from flask import request, render_template, url_for, flash, redirect, jsonify
from salonManagement import db, User, app, bcrypt, Employee, Appointment
from salonManagement.forms import SignUpForm , LoginForm
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, current_user, logout_user
from datetime import datetime


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/account")
def account():
    return render_template('account.html')


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    form1 = SignUpForm()
    form2 = LoginForm()
    if request.method == 'POST' and form1.validate_on_submit():
        usertype = request.form.get("usertype")
        emp_id = request.form.get("empid")
        name = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("pwd")

        new_user = User(accType=usertype, employee_id=emp_id,
                        username=name, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created! Please Log in to continue', 'success')

    if form2.validate_on_submit():
        user = User.query.filter_by(username=form2.username.data).first()
        if user and (user.password == form2.password.data):
            login_user(user, remember=form2.remember.data)
            return redirect(url_for('home'))

    return render_template('signup.html', title="signup", form1=form1, form2=form2)

#@app.route("/login", methods=['GET', 'POST'])
#def login():
#    form2 = LoginForm()
#   if form2.validate_on_submit():
 #       user = User.query.filter_by(username=form2.username.data).first()
  #      if user and bcrypt.check_password_hash(user.password, form2.pwd.data):
  #          login_user(user, render=form2.remember.data)
  #          return redirect(url_for('home'))
  #  
   # return render_template('signup.html', title="Loginin", form2=form2)

            

@app.route("/appointment", methods=['GET','POST'])
def appointment(): #can also get data by AJAX       

    if request.is_json:
        if request.method == 'POST':
            datepicked = request.json.get('date')
            print()
            print(datepicked)
            return jsonify({'date': datepicked})

    if request.method == 'POST':
        employee_name = request.form['employee_name']
        date = request.form['date']
        time = request.form['time']
        
        #employee = Employee.query.filter_by(employee_name=employee_name).first()
        current_username = current_user.username
        #if employee:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        time_obj = datetime.strptime(time, '%H:%M').time()

        appointment = Appointment (
                username=current_username,
                employee_name = employee_name,
                employee_id= '123',
                date = date_obj,
                time=time_obj
            )
        db.session.add(appointment)
        db.session.commit()

    employees = Employee.query.all()
    appointments = Appointment.query.all()
    users = User.query.all()

    return render_template("appointment.html", employees=employees, appointments=appointments, users=users)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))