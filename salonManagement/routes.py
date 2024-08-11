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
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_absolute_error
import numpy as np
import os

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
            flash('Welcom '+user.username+' ! You have Successfully Logged In', 'success')
            return redirect(url_for('home'))
            

    return render_template('login.html', title="login",form2=form2)

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
    return render_template("report_financial.html",active_tab='financial') 

@app.route("/report/appointment")
def report_appointments():
    return render_template("report_appointments.html",active_tab='appointments')

def load_customer_data():
    data = pandas.read_csv('C:\\Users\\HP\\Documents\\Project\\uniProject_year1\\salonManagement\\customer.csv')
    return data

@app.route("/report/customer_trends")
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

if __name__ == "__main__":
    app.run(debug=True)
