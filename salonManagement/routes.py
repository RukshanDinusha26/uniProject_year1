import json
from flask import request, render_template, url_for, flash, redirect, jsonify
from salonManagement import app, db, User, app, bcrypt, Employee, Appointment , Service, employee_service, login_manager, ADMIN_PASSWORD
from salonManagement.forms import SignUpForm , LoginForm
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from flask_login import login_user, current_user, logout_user, login_required
from datetime import datetime, time as dt_time, timedelta
from sqlalchemy import func
import time
import pandas 

import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import csv
from io import StringIO 
import base64
import io
from flask import session
import seaborn 
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import numpy as np
import os
from functools import wraps
import secrets
import stripe

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('You need to be logged in as an admin to access this page.', 'danger')
            return redirect(url_for('home'))
        if not session.get('is_admin'):
            flash('Admin access only.', 'danger')
            return redirect(url_for('home'))  
        return f(*args, **kwargs)
    return decorated_function

def employee_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('You need to be logged in as an Employee to access this page.', 'danger')
            return redirect(url_for('home'))
        if not session.get('is_employee'):
            flash('Employee access only.', 'danger')
            return redirect(url_for('home'))  
        return f(*args, **kwargs)
    return decorated_function


@app.route("/login", methods=['GET', 'POST'])
def login():
    time.sleep(1.5)
    form2 = LoginForm()
    if form2.validate_on_submit():
        hashed_admin_password = bcrypt.generate_password_hash(ADMIN_PASSWORD).decode('utf-8')
        user = User.query.filter_by(username=form2.username.data).first()
        if user and bcrypt.check_password_hash(hashed_admin_password,form2.password.data):
                session['is_admin'] = True
                login_user(user, remember=True)
                flash('Welcome ADMIN ! You have Successfully Logged In', 'success')
                return redirect(url_for('home'))
        
        if user and bcrypt.check_password_hash(user.password,form2.password.data):
                if user.employee_id:
                    session['is_employee'] = True
                    login_user(user, remember=True)
                    flash('Welcome'+user.username+'You have Successfully Logged In as an Employee!', 'success')
                    return redirect(url_for('home'))
                
                login_user(user, remember=True)
                flash('Welcome '+user.username+' ! You have Successfully Logged In', 'success')
                return redirect(url_for('home'))


    return render_template('login.html', title="login",form2=form2)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    time.sleep(1.5)
    form1 = SignUpForm()
    if form1.validate_on_submit():
        usertype = request.form.get("usertype")
        emp_id = request.form.get("empid")
        name = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("pwd")
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')


        new_user = User(
            username=name,
            email=email,
            password=hashed_password
        )

        if usertype == 'employee':
            existing_employee = Employee.query.filter_by(id=emp_id).first()
            
            if existing_employee:
                # If employee ID exists, create the employee user account
                new_user = User(
                    username=name,
                    email=email,
                    password=hashed_password,
                    employee_id = emp_id
                )
            else:
                # If employee ID does not exist, flash an error message
                flash('Employee ID does not exist. Please contact the admin.', 'danger')
                return render_template('signup.html', title="Signup", form1=form1)
            
        db.session.add(new_user)
        db.session.commit()

        flash('Your account has been created! Please log in to continue.', 'success')

    return render_template('signup.html', title="signup", form1=form1)



@app.route("/appointment/add", methods=['GET', 'POST'])
@login_required
def appointment_add():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('Unauthorized access. Please log in.', 'error')
            return redirect(url_for('login'))

        employee_id = request.form['employee_id']
        date = request.form['date']
        time = request.form['time']
        token = generate_secure_token()

        current_username = current_user.username
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        time_obj = datetime.strptime(time, '%H:%M').time()

        employee_id = request.form.get('employee_id')

        appointment = Appointment(
            token_number=token,
            username=current_username,
            employee_id=employee_id,
            date=date_obj,
            time=time_obj
        )
        print(appointment)
        db.session.add(appointment)
        db.session.commit()

        flash('Appointment added successfully!', 'success')

ALL_TIME_SLOTS = [
    "9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM"
]
@app.route('/get_available_times')
def get_available_times():
    try:
        agent_name = request.args.get('agent')
        date_str = request.args.get('date')
        date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else None

        if not agent_name or not date:
            return jsonify({'times': []})

        # Split the agent_name into first and last names if applicable
        name_parts = agent_name.split(' ', 1)  # Split on the first space
        if len(name_parts) != 2:
            return jsonify({'times': []})

        first_name, last_name = name_parts

        # Query to find the employee ID based on the agent's name
        employee = User.query.filter_by(firstname=first_name, lastname=last_name).first()

        if not employee:
            return jsonify({'times': []})

        employee_id = employee.employee_id

        # Convert time strings to datetime.time objects for comparison
        available_times = [dt_time(hour=int(slot.split(':')[0]), minute=int(slot.split(':')[1].split(' ')[0])) for slot in ALL_TIME_SLOTS]

        # Query existing appointments
        appointments = Appointment.query.filter_by(employee_id=employee_id, date=date).all()

        # Extract booked times
        booked_times = [appt.time for appt in appointments]

        # Determine available times by removing booked times
        available_times = [slot for slot in available_times if slot not in booked_times]

        # Convert available times back to string format
        available_times_str = [f"{t.strftime('%I:%M %p')}" for t in available_times]

        return jsonify({'times': available_times_str})

    except Exception as e:
        print(f"Error: {e}")  # Log the error for debugging
        return jsonify({'times': []})

def generate_secure_token():
    return secrets.randbelow(10**12)
    
@app.route("/appointment", methods=['GET','POST'])
def appointment(): 
    employees = db.session.query(Employee, User).join(User).all()
    services = Service.query.all()
    for service in services:
        service.agent_names = [
            f"{employee.user.firstname} {employee.user.lastname}" 
            for employee in service.employees
        ]
    print(employees)
    appointments = Appointment.query.all()
    users = User.query.all()

    return render_template("appointment.html", employees=employees, appointments=appointments, users=users, services=services)


@app.route('/book_appointment', methods=['POST'])
@login_required
def book_appointment():
    print(request.form)
    try:
        if not current_user.is_authenticated:
            flash('Unauthorized access. Please log in.', 'error')
            return redirect(url_for('login'))
        
        service_id = request.form.get('service_id')
        agent_name = request.form.get('agent')
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        print(service_id)

        date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else None
        time = datetime.strptime(time_str, '%I:%M %p').time() if time_str else None

        current_username = current_user.username

        name_parts = agent_name.split(' ', 1)
        if len(name_parts) != 2:
            flash('Invalid agent name.')
            return redirect(url_for('appointment'))

        first_name, last_name = name_parts
        employee = User.query.filter_by(firstname=first_name, lastname=last_name).first()

        if not employee:
            flash('Agent not found.')
            return redirect(url_for('appointment'))

        employee_id = employee.employee_id
        token = generate_secure_token()
        
        service = Service.query.filter_by(service_id=service_id).first()
        if not service:
            flash('Service not found.')
            print(service_id)
            return redirect(url_for('appointment'))

        service_id = service.service_id
        print(service)
        new_appointment = Appointment(
            token_number = token,
            username=current_username,
            employee_id=employee_id,
            service_id = service_id,
            date=date,
            time=time
        )
       
        db.session.add(new_appointment)
        db.session.commit()
        appointment_id = new_appointment.id

        session['appointment_proceed'] = True

        return redirect(url_for('appointment_proceed' ,token=token,service_id=service_id,appointment_id=appointment_id))

    except Exception as e:
        print(f"Error: {e}")  
        flash('An error occurred while booking the appointment.')

@app.route("/appointment/proceed")
@login_required
def appointment_proceed():

    if not session.get('appointment_proceed'):
        flash('Unauthorized access to this page.', 'error')
        return redirect(url_for('appointment'))

    token = request.args.get('token')
    service_id = request.args.get('service_id')
    appointment_id = request.args.get('appointment_id')
    service = Service.query.filter_by(service_id=service_id).first()
    appointment = Appointment.query.filter_by(id=appointment_id).first()
    
    session.pop('appointment_proceed', None)

    return render_template("appointment_proceed.html",token=token,service=service,appointment=appointment)



@app.route("/logout")
@login_required
def logout():
    session['is_admin'] = False
    session['is_employee'] = False
    logout_user()
    return redirect(url_for('home'))

@app.route("/account")
@login_required
def account():
    user = current_user  # Assuming current_user contains the logged-in user's details

    # Fetch pending appointments for the user
    pending_appointments = (
        db.session.query(Appointment, Service)
        .join(Service, Appointment.service_id == Service.service_id)
        .filter(Appointment.username == user.username, Appointment.payment_status == 'Pending')
        .all()
    )

    # Pass the user and appointments to the template
    return render_template('account.html', user=user, pending_appointments=pending_appointments)

@app.route("/account/settings")
def account_settings():
    user = current_user
    return render_template("accountSet_profile.html",active_tab="profile",user=user)

@app.route("/report")
@admin_required
def report():
    file_path = app.config['REPORT_FOLDER']
    append_to_csv_report(file_path)
    return render_template("report.html")

def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

@app.route("/report/financial")   
@admin_required
def report_financial():
    csv_file_path = 'C:\\Users\\HP\\Documents\\Project\\uniProject_year1\\salonManagement\\static\\reports\\appointment_report.csv'
    daily_report = []
    weekly_report = []
    monthly_report = []

    with open(csv_file_path, mode='r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            employee_name = row['Employee Name']
            time = row['Time']
            date = row['Date']
            payment = row['Payment']
            service_name = row['Service Name']
            
            daily_report.append({
                'employee': employee_name,
                'timeslot': time,
                'service': service_name,
                'payment': payment
            })
            weekly_report.append({
                'employee': employee_name,
                'week': 'Week 1',
                'service': service_name,
                'payment': payment
            })
            monthly_report.append({
                'employee': employee_name,
                'month': 'April',
                'service': service_name,
                'payment': payment
            })

    # Filter and sum only numeric values
    daily_total = sum(float(item['payment'].replace('$', '')) for item in daily_report if is_float(item['payment'].replace('$', '')))
    weekly_total = sum(float(item['payment'].replace('$', '')) for item in weekly_report if is_float(item['payment'].replace('$', '')))
    monthly_total = sum(float(item['payment'].replace('$', '')) for item in monthly_report if is_float(item['payment'].replace('$', '')))


    # Pass the data to the template
    return render_template('report_financial.html', 
                           daily_report=daily_report, 
                           weekly_report=weekly_report, 
                           monthly_report=monthly_report,
                           daily_total=daily_total,
                           weekly_total=weekly_total,
                           monthly_total=monthly_total,active_tab='financial')

@app.route("/report/appointment")
@admin_required
def report_appointments():
    return render_template("report_appointments.html",active_tab='appointments')

def load_customer_data():
    data = pandas.read_csv('C:\\Users\\HP\\Documents\\Project\\uniProject_year1\\salonManagement\\customer.csv')
    return data

@app.route("/report/customer_trends")
@admin_required
def report_customer_trends():
    data = load_customer_data()

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

    return render_template('report_customer_trends.html', age_plot_img=age_img_base, gender_plot_img=gender_img_base, violin_plot_img=violin_img_base,active_tab='customer')

def load_service_data():
    data = pandas.read_csv('C:\\Users\\HP\\Documents\\Project\\uniProject_year1\\salonManagement\\service.csv')
       
    data['Date'] = pandas.to_datetime(data['Date'], errors='coerce')
    data = data.dropna(subset=['Date'])
    return data

@app.route("/report_service_trends")
@admin_required
def report_service_trends():

    data = load_service_data()

    #total revenue by service
    plt.figure(figsize=(10, 5))
    revenue_data = data.groupby('Service')['Payment'].sum()
    revenue_data.plot(kind='bar', color='skyblue')
    plt.xlabel('Service')
    plt.ylabel('Total Revenue ($)')
    plt.grid(True)

    revenue_img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(revenue_img, format="png")
    revenue_img_base = base64.b64encode(revenue_img.getbuffer()).decode("ascii")

    #service distribution
    plt.figure(figsize=(8, 8))
    service_counts = data['Service'].value_counts()
    service_counts.plot(kind='pie', autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    plt.ylabel('')

    distri_img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(distri_img, format="png")
    distri_img_base = base64.b64encode(distri_img.getbuffer()).decode("ascii")
    
    #monthly service trends
    plt.figure(figsize=(10, 5))
    data['Month'] = data['Date'].dt.to_period('M')
    monthly_trends = data.groupby(['Month', 'Service']).size().unstack(fill_value=0)
    monthly_trends.plot(kind='line')
    plt.xlabel('Month')
    plt.ylabel('Number of Bookings')
    plt.grid(True)

    monthly_img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(monthly_img, format="png")
    monthly_img_base = base64.b64encode(monthly_img.getbuffer()).decode("ascii")

    plt.close()

    return render_template("report_service_trends.html",revenue_img_plot = revenue_img_base, distri_img_plot = distri_img_base,monthly_img_plot=monthly_img_base,active_tab='service')

@app.route("/report_predict_revenue")
@admin_required
def report_predict_revenue():
    data = pandas.read_csv('C:\\Users\\HP\\Documents\\Project\\uniProject_year1\\salonManagement\\income.csv')
    data['Date'] = pandas.to_datetime(data['Date'])
    
    data['Month'] = data['Date'].dt.month
    data['Year'] = data['Date'].dt.year
    monthly_revenue = data.groupby(['Year', 'Month']).agg({'Payment': 'sum'}).reset_index()
    monthly_revenue['Month_Year'] = monthly_revenue['Year'].astype(str) + '-' + monthly_revenue['Month'].astype(str).str.zfill(2)
    
    current_year = monthly_revenue['Year'].max()
    this_year_revenue = monthly_revenue[monthly_revenue['Year'] == current_year]

    this_year_revenue['Lag_1'] = this_year_revenue['Payment'].shift(1)
    this_year_revenue['Lag_2'] = this_year_revenue['Payment'].shift(2)
    this_year_revenue['Rolling_Mean_3'] = this_year_revenue['Payment'].rolling(window=3).mean()
    this_year_revenue.dropna(inplace=True)

    X = this_year_revenue[['Month', 'Lag_1', 'Lag_2', 'Rolling_Mean_3']]
    y = this_year_revenue['Payment']

    tscv = TimeSeriesSplit(n_splits=3)
    
    best_model = None
    best_mae = float("inf")

    for train_index, test_index in tscv.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]

        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)

        if mae < best_mae:
            best_mae = mae
            best_model = model

    last_month = this_year_revenue['Month'].max()
    last_lag_1 = this_year_revenue.iloc[-1]['Payment']
    last_lag_2 = this_year_revenue.iloc[-2]['Payment']
    last_rolling_mean = this_year_revenue['Rolling_Mean_3'].iloc[-1]

    future_months = []
    future_payments = []

    for i in range(1, 4):  
        new_month = last_month + i
        new_year = current_year
        if new_month > 12:
            new_month -= 12
            new_year += 1

        new_rolling_mean = (last_lag_1 + last_lag_2 + last_rolling_mean) / 3
        future_data = pandas.DataFrame({
            'Month': [new_month],
            'Lag_1': [last_lag_1],
            'Lag_2': [last_lag_2],
            'Rolling_Mean_3': [new_rolling_mean]
        })

        future_payment = best_model.predict(future_data)[0]
        future_months.append(f"{new_year}-{str(new_month).zfill(2)}")
        future_payments.append(future_payment)

        last_lag_2 = last_lag_1
        last_lag_1 = future_payment
        last_rolling_mean = new_rolling_mean


    future_revenue_df = pandas.DataFrame({
        'Month_Year': future_months,
        'Payment': future_payments
    })

    combined_revenue = pandas.concat([this_year_revenue[['Month_Year', 'Payment']], future_revenue_df], ignore_index=True)

    plt.figure(figsize=(12, 6))
    plt.plot(this_year_revenue['Month_Year'], this_year_revenue['Payment'], marker='o', label='Actual Revenue', color='blue')
    plt.plot(future_revenue_df['Month_Year'], future_revenue_df['Payment'], marker='x', linestyle='--', color='red', label='Predicted Revenue')
    plt.title(f'Monthly Revenue Prediction for {current_year}')
    plt.xlabel('Month-Year')
    plt.ylabel('Revenue ($)')
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)

    predict_img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(predict_img, format='png')
    predict_img_base = base64.b64encode(predict_img.getbuffer()).decode('ascii')
    plt.close()

    return render_template("report_revenue_predict.html", predict_img_plot=predict_img_base,active_tab='revenue')

@app.route("/admin-panel")
@admin_required
def adminPanel():

    return render_template("admin-panel.html")

@app.route("/admin-panel/appointments",methods=['POST','GET'])
@admin_required
def adminPanel_appointments():
    today = datetime.today().date()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    
    # Fetch appointments for yesterday, today, and tomorrow
    appointments_yesterday = (
        db.session.query(Appointment, Service)
        .join(Service, Appointment.service_id == Service.service_id)
        .filter(Appointment.date == yesterday)
        .all()
    )
    appointments_today = (
        db.session.query(Appointment, Service)
        .join(Service, Appointment.service_id == Service.service_id)
        .filter(Appointment.date == today)
        .all()
    )
    appointments_tomorrow = (
        db.session.query(Appointment, Service)
        .join(Service, Appointment.service_id == Service.service_id)
        .filter(Appointment.date == tomorrow)
        .all()
    )

    
    list_appointments = {
        'yesterday': [],
        'today': [],
        'tomorrow': []
    }
    
    for appointment in appointments_yesterday:
            list_appointments['yesterday'].append(appointment)

    for appointment in appointments_today:
            list_appointments['today'].append(appointment)

    for appointment in appointments_tomorrow:
            list_appointments['tomorrow'].append(appointment)
    
    if request.method == 'POST':
        appointment_id = request.form.get('appointment_id')
        status = request.form.get('status')
        payment_status = request.form.get('payment_status')

        if not appointment_id or not appointment_id.isdigit():
            flash('Please Select an Appointment to update!', 'error')
            return redirect(url_for('adminPanel_appointments'))
        
        # Update appointment status
        appointment = db.session.query(Appointment).filter_by(id=appointment_id).first()
        if appointment:
            appointment.status = status
            appointment.payment_status = payment_status
            db.session.commit()
        
        return redirect(url_for('adminPanel_appointments'))

    return render_template(
        'admin-appointments.html',
        list_appointments=list_appointments,
        yesterday=yesterday,
        today=today,
        tomorrow=tomorrow,
        active_tab='appointments'
    )
    

@app.route("/admin-panel/employee",methods=['GET','POST'])
@admin_required
def adminPanel_employee():
    print(request.form)
    if request.method == 'POST':
        employee_id = request.form.get('employeeId')

        existing_employee = Employee.query.filter_by(id=employee_id).first()
        if existing_employee:
            flash("Employee with this ID already exists.", "error")

        new_employee = Employee(id=employee_id)
        db.session.add(new_employee)
        db.session.commit()

        flash("Employee has Sucessfully added!",'sucess')
        return redirect(url_for('adminPanel_employee'))
    
    employees = db.session.query(Employee, User).join(User).all()
    return render_template("admin-employee.html",active_tab='employees',employees=employees)

@app.route('/admin-panel/services', methods=['GET', 'POST'])
@admin_required
def adminPanel_services():
    if request.method == 'POST':
        service_name = request.form['service_name']
        service_price = request.form['service_price']
        service_image = request.files['service_image']

        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        max_service_id = db.session.query(func.max(Service.service_id)).scalar()

        new_service_id = max_service_id + 1 if max_service_id else 1

        if service_image:
            filename = secure_filename(service_image.filename)
            service_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            new_service = Service(service_id=new_service_id,service_name=service_name, price=service_price, service_image=filename)
            db.session.add(new_service)
            db.session.commit()

            flash('Service created successfully!', 'success')
            return redirect(url_for('adminPanel_services'))

    services = Service.query.all()
    return render_template('admin-service.html', services=services, active_tab="service")


@app.route("/account-settings/profile",methods=['GET','POST'])
@login_required
def accountSet_profile():
    user = current_user
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        fname = request.form['fname']
        lname = request.form['lname']
        about = request.form['about']
        
        # Check if an image was uploaded
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file.filename:  # If a file was uploaded
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['PROFILE_UPLOAD_FOLDER'], filename))
                user.profile_image = filename
        
        user.username = username
        user.email = email
        user.firstname = fname
        user.lastname = lname
        user.about = about

        db.session.commit()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('accountSet_profile'))
    return render_template("accountSet_profile.html",active_tab='profile',user=user)


@app.route("/account-settings/personal",methods=['GET','POST'])
@login_required
def accountSet_personal():
    user = current_user
    if request.method == 'POST':
        dob = request.form.get('dob')
        age = request.form.get('age')
        gender = request.form.get('gender')
        address = request.form.get('about')

        # Update user information
        user.dob = dob
        user.age = age
        user.gender = gender
        user.address = address

        # Commit the changes to the database
        db.session.commit()

        flash('Personal information updated successfully!', 'success')
        return redirect(url_for('accountSet_personal'))

    return render_template("accountSet_personal.html", active_tab='personal', user=user)


@app.route("/account-settings/account",methods=['GET','POST'])
@login_required
def accountSet_account():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if current_user.password != current_password:
            flash('Current password is incorrect.', 'error')
            return redirect(url_for('accountSet_account'))

        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return redirect(url_for('accountSet_account'))

        # Update the password
        current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()

        flash('Password changed successfully!', 'success')
        return redirect(url_for('accountSet_account'))
    
    return render_template("accountSet_account.html",active_tab='account')

@app.route('/appointments/schedule')
def appointments_schedule():
    today = datetime.today().date()
    tomorrow = today + timedelta(days=1)
    
    # Fetch appointments for today and tomorrow
    appointments_today = (
        db.session.query(Appointment, Service)
        .join(Service, Appointment.service_id == Service.service_id)
        .filter(Appointment.date == today)
        .all()
    )
    appointments_tomorrow= (
        db.session.query(Appointment, Service)
        .join(Service, Appointment.service_id == Service.service_id)
        .filter(Appointment.date == tomorrow)
        .all()
    )
    
    # Group appointments by employee
    employees = db.session.query(Employee, User).join(User).all()
    employee_appointments = {employee.Employee.id: {'today': [], 'tomorrow': []} for employee in employees}

    for appointment in appointments_today:
        employee_appointments[appointment.Appointment.employee_id]['today'].append(appointment)

    for appointment in appointments_tomorrow:
        employee_appointments[appointment.Appointment.employee_id]['tomorrow'].append(appointment)

    return render_template(
        'appointment_schedule.html',
        employees=employees,
        employee_appointments=employee_appointments,
        today=today,
        tomorrow=tomorrow
    )

@app.route('/appointments/manage', methods=['GET', 'POST'])
@employee_required
def manage_appointments():
    today = datetime.today().date()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    
    # Fetch appointments for yesterday, today, and tomorrow
    appointments_yesterday = (
        db.session.query(Appointment, Service)
        .join(Service, Appointment.service_id == Service.service_id)
        .filter(Appointment.date == yesterday)
        .all()
    )
    appointments_today = (
        db.session.query(Appointment, Service)
        .join(Service, Appointment.service_id == Service.service_id)
        .filter(Appointment.date == today)
        .all()
    )
    appointments_tomorrow = (
        db.session.query(Appointment, Service)
        .join(Service, Appointment.service_id == Service.service_id)
        .filter(Appointment.date == tomorrow)
        .all()
    )

    user = current_user
    user_id = user.id 
    employee = (db.session.query(Employee, User)
            .join(User, Employee.user)
            .filter(User.id == user_id)
            .first())

    
    employee_appointments = {
        'yesterday': [],
        'today': [],
        'tomorrow': []
    }
    
    for appointment in appointments_yesterday:
        if appointment.Appointment.employee_id == employee.User.employee_id:
            employee_appointments['yesterday'].append(appointment)

    for appointment in appointments_today:
        if appointment.Appointment.employee_id == employee.User.employee_id:
            employee_appointments['today'].append(appointment)

    for appointment in appointments_tomorrow:
        if appointment.Appointment.employee_id == employee.User.employee_id:
            employee_appointments['tomorrow'].append(appointment)
    
    if request.method == 'POST':
        appointment_id = request.form.get('appointment_id')
        status = request.form.get('status')
        payment_status = request.form.get('payment_status')

        if not appointment_id or not appointment_id.isdigit():
            flash('Please Select an Appointment to update!', 'error')
            return redirect(url_for('manage_appointments'))
        
        # Update appointment status
        appointment = db.session.query(Appointment).filter_by(id=appointment_id).first()
        if appointment:
            appointment.status = status
            appointment.payment_status = payment_status
            db.session.commit()
        
        return redirect(url_for('manage_appointments'))

    return render_template(
        'manage_appointments.html',
        employee_appointments=employee_appointments,
        yesterday=yesterday,
        today=today,
        tomorrow=tomorrow
    )

@app.route('/employees/delete', methods=['GET','POST'])
@admin_required
def delete_employee():
    # Find the employee to delete
    
    employee_id = request.form.get('employee_id')
    print(employee_id)
    employee = Employee.query.filter_by(id=employee_id).first()


    db.session.delete(employee)
    db.session.commit()

    flash(f"Employee {employee_id} deleted successfully.", "success")
    return redirect(url_for("adminPanel_employee"))

@app.route('/delete_service', methods=['POST'])
@admin_required
def delete_service():
    service_id = request.form['service_id']
    service = Service.query.get(service_id)
    if service:
        # Delete image file if exists
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], service.service_image))
        except Exception as e:
            print(f"Error deleting image: {e}")
        
        db.session.delete(service)
        db.session.commit()
        flash('Service deleted successfully!', 'success')
    else:
        flash('Service not found!', 'danger')

    return redirect(url_for('adminPanel_services'))

@app.route('/services/update', methods=['POST'])
@admin_required
def update_service():
    service_id = request.form['service_id']
    service = Service.query.get(service_id)

    service_name = request.form['service_name']
    service_price = request.form['service_price']

    # Check if a new image was uploaded
    file = request.files['service_image']
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        service.service_image = filename

    service.service_name = service_name
    service.price = service_price

    db.session.commit()
    flash('Service updated successfully!', 'success')
    return redirect(url_for('adminPanel_services'))

@app.route('/admin/assign-services', methods=['GET', 'POST'])
@admin_required
def adminPanel_assign_services():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        service_id = request.form.get('service_id')

        employee = Employee.query.get(employee_id)
        service = Service.query.get(service_id)

        if employee and service:
            employee.services.append(service)
            db.session.commit()
            flash('Service assigned successfully!', 'success')
        else:
            flash('Invalid Employee ID or Service ID.', 'danger')

    
        return redirect(url_for('adminPanel_assign_services'))

    employees = Employee.query.all()
    services = Service.query.all()
    employee_services = db.session.query(employee_service).all()
    return render_template('admin-assign_service.html', employees=employees, services=services, employee_services=employee_services,active_tab='assign_service')

@app.route('/admin/remove-service', methods=['POST'])
@admin_required
def remove_service():
    employee_id = request.form.get('employee_id')
    service_id = request.form.get('service_id')

    
    employee = Employee.query.get(employee_id)
    service = Service.query.get(service_id)

    if employee and service:
        db.session.execute(
                employee_service.delete().where(
                    (employee_service.c.employee_id == employee_id) &
                    (employee_service.c.service_id == service_id)
                ))
        db.session.commit()
        flash('Service removed successfully!', 'success')
    
    else:
        flash('Invalid Employee ID or Service ID.', 'danger')
        

    return redirect(url_for('adminPanel_assign_services'))



@app.route("/account/delete", methods=['POST'])
@login_required
def delete_account():
    if current_user.is_authenticated:
        db.session.delete(current_user)
        db.session.commit()

        flash('Account deleted successfully!', 'success')
        return redirect(url_for('home'))  

    flash('You must be logged in to delete your account.', 'error')
    return redirect(url_for('login'))  

def append_to_csv_report(file_path):
    # Query the database to get appointment details along with related user, employee, and service data
    appointments = Appointment.query.options(
        joinedload(Appointment.employee),
        joinedload(Appointment.service),
        joinedload(Appointment.employee).joinedload(Employee.user)
    ).all()

    # Create an in-memory string buffer
    output = StringIO()
    writer = csv.writer(output)

    # Write data rows
    for appointment in appointments:
        employee_name = f"{appointment.employee.user.firstname} {appointment.employee.user.lastname}"
        service_name = appointment.service.service_name
        user_gender = appointment.employee.user.gender
        user_age = appointment.employee.user.age
        
        writer.writerow([
            employee_name,
            f"{appointment.time}",
            f"{appointment.date}",
            appointment.payment_status,
            user_gender,
            service_name,
            user_age
        ])

    # Reset buffer position to the beginning
    output.seek(0)

    # Append data to the existing CSV file or create it if it does not exist
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            # Write the header if the file is being created for the first time
            writer.writerow(['Employee Name', 'Time', 'Date', 'Payment Status', 'User Gender', 'Service Name', 'User Age'])
        # Write the new data rows
        file.write(output.getvalue())

@app.route("/create-checkout-session", methods=['POST'])
@login_required
def create_checkout_session():
    try:
        service_id = request.form.get('service_id')
        service = Service.query.filter_by(service_id=service_id).first()

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'lkr',  
                    'product_data': {
                        'name': service.service_name,
                    },
                    'unit_amount': int(service.price), 
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('payment_success', appointment_id=request.form.get('appointment_id'), _external=True),
            cancel_url=url_for('payment_cancel', appointment_id=request.form.get('appointment_id'), _external=True),
        )

        return jsonify({'id': session.id})

    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route("/payment-success")
@login_required
def payment_success():
    appointment_id = request.args.get('appointment_id')

    # Update the appointment to reflect successful payment
    appointment = Appointment.query.get(appointment_id)
    appointment.payment_status = 'Paid'
    db.session.commit()

    flash('Payment successful!', 'success')
    return render_template('sucess.html')

@app.route("/payment-cancel")
@login_required
def payment_cancel():
    flash('Payment canceled.', 'error')
    return render_template('fail.html')
