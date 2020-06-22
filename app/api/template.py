from flask import render_template

from app import app


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/employee/travels')
def employee_travel():
    return render_template('employee/travels.html')

@app.route('/manager/travels')
def manager_travel():
    return render_template('manager/travels.html')

@app.route('/finance/travels')
def finance_travel():
    return render_template('finance/travels.html')

@app.route('/administrator/dashboard')
def administrator_dashboard():
    return render_template('administration/dashboard.html')
