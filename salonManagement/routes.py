import json
from flask import request, render_template, url_for, flash, redirect, jsonify
from salonManagement import db, User, app, bcrypt, Employee, Appointment
from salonManagement.forms import SignUpForm , LoginForm
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, current_user, logout_user
from datetime import datetime
from sqlalchemy import func
import time
import pandas 
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import io
import base64
import seaborn 

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    time.sleep(1.5)
    form2 = LoginForm()
    if form2.validate_on_submit():
        user = User.query.filter_by(username=form2.username.data).first()
        if user and (user.password == form2.password.data):
            login_user(user, remember=form2.remember.data)
            return redirect(url_for('home'))

    return render_template('login.html', title="login",form2=form2)

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    time.sleep(1.5)
    form1 = SignUpForm()
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

    return render_template('signup.html', title="signup", form1=form1)

@app.route("/appointment/add",methods=['GET', 'POST'])         
def appointmentAdd():
    if request.method == 'POST':
        employee_name = request.form.get('appEmp')
        date = request.form.get('appDate')
        time = request.form.get('appTime')
        print(employee_name)
        print(date)
        print(time)
    
        #dont use employee = Employee.query.filter_by(employee_name=employee_name).first()
        current_username = current_user.username
        #dont use if employee:
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

        return jsonify({'user':current_username})
    

@app.route("/appointment", methods=['GET','POST'])
def appointment(): #can also get data by AJAX       

    if request.is_json:
        if request.method == 'POST':
            datepicked = request.json.get('date')
            selectedEmployee = request.json.get('selectedEmp')
            print()
            print(datepicked)
            print(selectedEmployee)
            datepicked_obj = datetime.strptime(datepicked,'%Y-%m-%d').date()
            appt = Appointment.query.filter(Appointment.date.like(datepicked_obj), Appointment.employee_name.like(selectedEmployee)).all()
            print(appt)

            hours = [8,9,10,11,12,13,14,15,16,17]
            for appt_item in appt:
                time_obj = db.session.query(func.strftime('%H',appt_item.time)).first()
                print(time_obj)
                i = int(time_obj[0])

                if i in hours:
                    hours = [x for x in hours if x !=i ]
            return jsonify({'hours': hours})
    

    employees = Employee.query.all()
    appointments = Appointment.query.all()
    users = User.query.all()

    return render_template("appointment.html", employees=employees, appointments=appointments, users=users)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/account")
def account():
    return render_template("account.html")

@app.route("/account/settings")
def account_settings():
    return render_template("accountSet.html")

@app.route("/report")
def report():
    return render_template("report.html")

@app.route("/report/financial")   
def report_financial():
    return render_template("report_financial.html") 

@app.route("/report/appointment")
def report_appointments():
    return render_template("report_appointments.html")

def load_data():
    data = pandas.read_csv('C:\\Users\\HP\\Documents\\Project\\uniProject_year1\\salonManagement\\customer.csv')
    return data

@app.route("/report/customer_trends")
def report_customer_trends():
    data = load_data()

    age_groups = pandas.cut(data['age'], bins=[0, 18, 30, 40, 50, 60, 100], 
                        labels=['0-18', '19-30', '31-40', '41-50', '51-60', '61+'])
    age_distribution = age_groups.value_counts().sort_index()

    gender_distribution = data['gender'].value_counts()

    fig, ax = plt.subplots(figsize=(8, 6))
    seaborn.violinplot(x='gender', y='age', data=data, hue='gender', ax=ax, palette='pastel', legend=False)
    
    y_min, y_max = ax.get_ylim()
    y_values = range(int(y_min), int(y_max) + 1) 

    for y in y_values:
        ax.axhline(y=y, color='lightgray', linestyle='-', linewidth=0.5)

    ax.set_xlabel('Gender')
    ax.set_ylabel('Age')

    violin_img = io.BytesIO()
    plt.savefig(violin_img, format='png')
    violin_img.seek(0)
    violin_img_base = base64.b64encode(violin_img.getvalue()).decode('utf-8')

    plt.close()


    fig_age, ax_age = plt.subplots(figsize=(8, 6))
    age_distribution.plot(kind='bar', ax=ax_age, color='skyblue')
    ax_age.set_xlabel('Age Group')
    ax_age.set_ylabel('Count')

    age_img = io.BytesIO()
    plt.savefig(age_img, format='png')
    age_img.seek(0)
    age_img_base = base64.b64encode(age_img.getvalue()).decode('utf-8')

    plt.close(fig_age)

    fig_gender, ax_gender = plt.subplots(figsize=(8, 6))
    gender_distribution.plot(kind='pie', ax=ax_gender, autopct='%1.1f%%', colors=['lightcoral', 'lightblue'])

    gender_img = io.BytesIO()
    plt.savefig(gender_img, format='png')
    gender_img.seek(0)
    gender_img_base = base64.b64encode(gender_img.getvalue()).decode('utf-8')

    plt.close(fig_gender)

    return render_template('report_customer_trends.html', age_plot_img=age_img_base, gender_plot_img=gender_img_base, violin_plot_img=violin_img_base)
