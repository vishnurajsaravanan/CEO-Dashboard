# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
import datetime
import time
from matplotlib import pyplot as plt
from sqlalchemy import func
from flask import render_template, redirect, request, session, url_for, g, jsonify, render_template_string
from flask_login import (
    current_user,
    login_user,
    logout_user,
    login_required
)
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import firebase_admin
from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import AssignTask, FinanceChat, OperationalChat, SalesChat, Users, FinancialMetrics, SalesMetrics, OperationalMetrics, ChatMessages, KaggleData, Tasks, Notification

from apps.authentication.util import verify_pass
from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd


# landing page

@blueprint.route('/')
def index():
    return render_template("homepage/index.html")

@blueprint.route('/home')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))

# login

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        department = request.form.get('department')
        # Locate user
        user = Users.query.filter_by(username=username).first()

        # Check the password
        if user and verify_pass(password, user.password):
            login_user(user)
            if role == "CEO":
                return redirect(url_for('authentication_blueprint.ceo_dashboard'))
            elif role == "Manager":
                return redirect(url_for('authentication_blueprint.manager_dashboard'))
            elif role == "Employee":
                return redirect(url_for('authentication_blueprint.employee_dashboard'))
            return redirect(url_for('authentication_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg='Wrong user or password',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('authentication_blueprint.login'))

# register

@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        role = request.form.get('role')
        if role=="CEO":
            department = None
        else:
            department = request.form.get('department')


        # Check usename exists
        user = Users.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Username already registered',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        mail = Users.query.filter_by(email=email).first()
        if mail:
            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_account_form)
        
        # Check phone exists
        ph = Users.query.filter_by(phone=phone).first()
        if ph:
            return render_template('accounts/register.html',
                                   msg='Phone number already exists',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user
        user = Users(**request.form)
        db.session.add(user)
        db.session.commit()

        # Delete user from session
        logout_user()
        
        return render_template('accounts/register.html',
                               msg='Account created successfully.',
                               success=True,
                               form=create_account_form)

    else:
        return render_template('accounts/register.html', form=create_account_form)

# logout

@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))

# financial page

@blueprint.route('/financial')
def financial():
    if current_user.role == "Employee" and current_user.department == "Finance":
        return render_template('employee/financial-metrics.html')
    elif current_user.role == "CEO":
        return render_template('ceo/get_metrics.html')
    elif current_user.role == "Manager" and current_user.department == "Finance":
        return render_template('manager/financial-ratios.html')

# sales page
    
@blueprint.route('/sales')
@login_required
def sales():
    if current_user.role == "Employee" and current_user.department == "Sales":
        return render_template('employee/sales-metrics.html', segment='sales')
    elif current_user.role == "CEO":
        return render_template('ceo/get_sales.html', segment='sales')
    elif current_user.role == "Manager" and current_user.department == "Sales":
        return render_template('manager/get_sales.html', segment='sales')
    

# Operational page

@blueprint.route('/operational')
@login_required
def operational():
    if current_user.role == "Employee" and current_user.department == "Operational":
        return render_template('employee/operational_metrics.html', segment='operational')
    elif current_user.role == "CEO":
        return render_template('ceo/get_operational.html', segment='operational')
    elif current_user.role == "Manager" and current_user.department == "Operational":
        return render_template('manager/get_operational.html', segment='operational')
    

# Chat page

@blueprint.route('/chat')
@login_required
def chat():
    if current_user.role == "Employee":
        return render_template('employee/chat_message.html', segment='chat')
    elif current_user.role == "CEO":
        return render_template('ceo/chat_message.html', segment='chat')
    elif current_user.role == "Manager":
        return render_template('manager/chat_message.html', segment='chat')
    

# EMAIL page

@blueprint.route('/email')
@login_required
def email():
    if current_user.role == "Employee":
        return render_template('employee/send_email.html', segment='email')
    elif current_user.role == "CEO":
        return render_template('ceo/send_email.html', segment='email')
    elif current_user.role == "Manager":
        return render_template('manager/send_email.html', segment='email')

@blueprint.route('/tasks')
@login_required
def tasks():
    data = Users.query.all()
    task = Tasks.query.all()
    # if current_user.role == "Employee":
    #     return render_template('employee/get_tasks.html', segment='tasks')
    if current_user.role == "CEO":
        return render_template('ceo/task_allocation.html', segment='tasks', data=data, task=task)
    # elif current_user.role == "Manager":
    #     return render_template('manager/get_tasks.html', segment='tasks')
    

@blueprint.route('/assign_tasks')
@login_required
def assign_tasks():
    data = Users.query.all()
    task = AssignTask.query.all()
    if current_user.role == "Employee":
        return render_template('employee/manager_task.html', segment='assign_tasks',task = task)
    elif current_user.role == "Manager":
        return render_template('manager/assign_tasks.html', segment='assign_tasks',  data=data, task = task,status='Message sent successfully')

# tasks allocation
@blueprint.route('/create_tasks', methods=['GET','POST'])
@login_required
def task_allocation():
    if request.method == "POST":
        if current_user.role == "CEO":
            username = request.form.get('user')
            task = request.form.get('tasks')
            is_checked = False
            taskAllocation = Tasks(
                username=username,
                task=task,
                is_checked=is_checked
            )
            db.session.add(taskAllocation)
            db.session.commit()
            time.sleep(2)
            return redirect('ceo/dashboard')
        else:
            return jsonify({"message": "User not found"})
        
    elif request.method == "GET":
        task_given = Tasks.query.all()
        if current_user.role == "CEO":
            return render_template("ceo/task_allocation.html",task_given = task_given)
        elif current_user.role == "Employee":
            return render_template("employee/task_allocation.html",task_given = task_given)
        elif current_user.role == "Manager":
            return render_template("manager/task_allocation.html",task_given = task_given)


# tasks allocation
@blueprint.route('/assign_tasks', methods=['GET','POST'])
@login_required
def allocation_tasks():
    if request.method == "POST":
        if current_user.role == "Manager":
            username = request.form.get('user')
            task = request.form.get('tasks')
            is_checked = False
            taskAllocation = AssignTask(
                username=username,
                task=task,
                department=current_user.department,
                is_checked=is_checked
            )
            db.session.add(taskAllocation)
            db.session.commit()
            time.sleep(2)
            return redirect('manager/dashboard')
        else:
            return jsonify({"message": "User not found"})
        
    elif request.method == "GET":
        task_give = AssignTask.query.all()
        send_email("Vishnu","gdscsnscollegeofengineering@gmail.com", 'Task Notification from your organization','Task Status from growth organization' + str([[row.id, row.username, row.task, row.department, "Completed"] for row in task_give]))
        if current_user.role == "Employee":
            return render_template("employee/manager_task.html",task_given = task_give)
        elif current_user.role == "Manager":
            return render_template("manager/assign_tasks.html",task_given = task_give)



# Send email

@blueprint.route('/send_email', methods=['POST'])
def send_email():
    # Email configuration
    sender_email = 'MAIL_ID'
    sender_password = 'PASSSWORD'
    recipient_email = request.form.get('recipient_email')
    subject = request.form.get('subject')
    message = request.form.get('message_body')
    # Establish a secure SMTP connection with the SMTP server
    try:
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        # Establish a secure SMTP connection with the SMTP server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, recipient_email, msg.as_string())
        time.sleep(2)
        if current_user.role == "CEO":
            return redirect('ceo/dashboard')
        elif current_user.role == "Manager":
            return redirect('manager/dashboard')
        elif current_user.role == "Employee":
            return redirect('employee/dashboard')
    except Exception as e:
        return jsonify({'message': f'Error sending email: {str(e)}'})

    finally:
        server.quit()
        return redirect(url_for('authentication_blueprint.'+ current_user.role.lower() +'_dashboard'))



# attach files

@blueprint.route('/attach')
def attach_files():
    if current_user.role == "Employee":
        return render_template('employee/attach_file.html', segment='file')
    elif current_user.role == "CEO":
        return render_template('ceo/attach_file.html', segment='file')
    elif current_user.role == "Manager":
        return render_template('manager/attach_file.html', segment='file')


# text notification

def notification_display(username, message):
    content = "{username}-{message}".format(username=username, message=message)
    text__notification = Notification(
        username=username,
        message=message
    )
    db.session.add(text__notification)
    db.session.commit()
    return content



# email notification

def send_mail(username, email, subject, message):
    content = """
        Hello {username}! \n
        {message}\n
        This message is automated.\n
        Growth Dashboard!""".format(username=username, message=message)
    mail=smtplib.SMTP('smtp.gmail.com', 587)
    mail.ehlo()
    mail.starttls()
    sender='vishnubuddie02@gmail.com'
    recipient=email
    mail.login(sender,'moszomgzrzyzzrrx')
    header='To:'+recipient+'\n'+'From:' +sender+'\n'+'subject:'+subject+'\n'
    content=header+content
    mail.sendmail(sender, recipient, content)
    mail.close()
    print("Email sent successfully!")

# Financial Metrics

@blueprint.route('/calculate_metrics', methods=['POST'])
def calculate_metrics():
    # user_id = Users.query.get('id')
    if request.method == 'POST':
        # Assuming you have a user_id in the form
        revenue = float(request.form.get('revenue'))
        profit = float(request.form.get('profit'))
        expenses = float(request.form.get('expenses'))

        # Create a new FinancialMetrics instance and add it to the database
        financialmetrics = FinancialMetrics(
            revenue=revenue,
            profit=profit,
            expenses=expenses
        )

        db.session.add(financialmetrics)
        db.session.commit()

        notification_display(current_user.username,'Added Financial Metrics')
        # mail to manager
        send_mail("Vishnu", 'vishnurajs.personal@gmail.com', 'Submission of Financial Data', "I've added the financial data" )
        time.sleep(2)

        return redirect('employee/dashboard')
    else:
        return jsonify({"message": "User not found"})


# Sales Metrics

@blueprint.route('/calculate_sales', methods=['POST'])
def calculate_sales():
    # user_id = Users.query.get(id)
    if request.method == 'POST':
        # Assuming you have a user_id in the form
        sales_revenue = float(request.form.get('sales_revenue'))
        conversion = float(request.form.get('conversion'))
        acquisition = float(request.form.get('acquisition'))
        lifetime = float(request.form.get('lifetime'))
        churn = float(request.form.get('churn'))
        s_roi = float(request.form.get('s_roi'))

        # Create a new FinancialMetrics instance and add it to the database
        sales_metrics = SalesMetrics(
            # id=id,
            # user_id=user_id,  # Set the username from the user object
            sales_revenue=sales_revenue,
            conversion=conversion,
            acquisition=acquisition,
            lifetime=lifetime,
            churn=churn,
            s_roi=s_roi
        )

        db.session.add(sales_metrics)
        db.session.commit()
        notification_display(current_user.username,'Added sales Metrics')
        # mail to manager
        send_mail("Vishnu", 'vishnurajs.personal@gmail.com', 'Submission of sales Data', "I've added the sales data" )
        time.sleep(2)
        return redirect('employee/dashboard')
    else:
        return jsonify({"message": "User not found"})



# Operational metrics

@blueprint.route('/operational_metrics', methods=['POST'])
def operational_metrics():
    if request.method == 'POST':
        # Retrieve data from the form fields
        total_production_output = float(request.form.get('total_production_output'))
        supplier_performance = float(request.form.get('supplier_performance'))
        downtime_percentage = float(request.form.get('downtime_percentage'))
        

        # Create an instance for all operational metrics in a single table
        operational_metrics = OperationalMetrics(
            total_production_output=total_production_output,
            supplier_performance=supplier_performance,
            downtime_percentage=downtime_percentage
        )

        # Add and commit the metrics to the database
        db.session.add(operational_metrics)
        db.session.commit()
        notification_display(current_user.username,'Added operational Metrics')
        # mail to manager
        send_mail("Vishnu", 'vishnurajs.personal@gmail.com', 'Submission of operational Data', "I've added the operational data" )
        time.sleep(2)
        return redirect('employee/dashboard')
    else:
        return jsonify({"message": "User not found"})
    

# Operational data

@blueprint.route('/get_operational', methods=['GET'])
@login_required
def get_operational():

    data = OperationalMetrics.query.all()
    
    total_production_output = db.session.query(func.sum(OperationalMetrics.total_production_output)).scalar()
    supplier_performance = db.session.query(func.sum(OperationalMetrics.supplier_performance)).scalar()
    downtime_percentage = db.session.query(func.sum(OperationalMetrics.downtime_percentage)).scalar()
    
    inventory_turnover = total_production_output/downtime_percentage

    send_mail("Vishnuraj", "gdscsnscollegeofengineering@gmail.com","Operational report","Operational Data of your organization\n\n"+'Total Production Output : '+str(total_production_output)+'\nSupplier Performance : '+str(supplier_performance)+'\nDowntime Percentage : '+str(downtime_percentage)+'\nInventory Turnover : '+str(inventory_turnover))
    if current_user.role=="CEO":
        return render_template("ceo/get_operational.html",
                                data=data,
                                inventory_turnover = inventory_turnover,
                                total_production_output = total_production_output,
                                downtime_percentage = downtime_percentage,
                                supplier_performance = supplier_performance,
                                )
    
    elif current_user.role=="Manager":
        return render_template("manager/get_operational.html",
                                data=data,
                                inventory_turnover = inventory_turnover,
                                total_production_output = total_production_output,
                                downtime_percentage = downtime_percentage,
                                supplier_performance = supplier_performance
                                )
    
    else:
        return "Invalid request method"


# Financial Data

@blueprint.route('/get_metrics', methods=['GET'])
@login_required
def get_metrics():
    # kaggle()
    data = FinancialMetrics.query.all()
    
    total_revenue = db.session.query(func.sum(FinancialMetrics.revenue)).scalar()
    total_expenses = db.session.query(func.sum(FinancialMetrics.expenses)).scalar()
    total_profit = db.session.query(func.sum(FinancialMetrics.profit)).scalar()

    gross_profit = (total_profit / total_revenue) * 100
    net_profit = (total_expenses / total_revenue) * 100
    current_ratio = total_revenue / total_expenses
    quick_ratio = gross_profit - total_expenses
    debt_equity = total_expenses/total_revenue
    debt_asset = total_expenses/total_profit
    send_mail("Vishnuraj", "gdscsnscollegeofengineering@gmail.com","Financial report","Financial Data of your organization\n\n"+'Gross Profit : '+str(gross_profit)+'Net Profit : '+str(net_profit)+ 'Current Ratio : '+str(current_ratio)+'Quick Ratio : ' +str(quick_ratio)+'Debt Equity : '+str(debt_equity)+'Debt Asset : '+str(debt_asset))

    if current_user.role=="CEO":
        return render_template("ceo/get_metrics.html",
                            data=data,
                            gross_profit=gross_profit,
                            net_profit=net_profit,
                            current_ratio=current_ratio,
                            quick_ratio=quick_ratio,
                            debt_equity=debt_equity,
                            debt_asset=debt_asset,
                            total_revenue=total_revenue)
    
    elif current_user.role=="Manager":
        return render_template("manager/financial-ratios.html",
                                data=data,
                                gross_profit=gross_profit,
                                net_profit=net_profit,
                                current_ratio=current_ratio,
                                quick_ratio=quick_ratio,
                                debt_equity=debt_equity,
                                debt_asset=debt_asset
                                )
    else:
        return "Invalid request method"
    

# Sales data

@blueprint.route('/get_sales', methods=['GET'])
@login_required
def get_sales():

    data = SalesMetrics.query.all()

    total_id = db.session.query(func.sum(SalesMetrics.id)).scalar()
    total_sales_revenue = db.session.query(func.sum(SalesMetrics.sales_revenue)).scalar()
    conversion_rates = db.session.query(func.sum(SalesMetrics.conversion)).scalar()
    cac = db.session.query(func.sum(SalesMetrics.acquisition)).scalar()
    clv = db.session.query(func.sum(SalesMetrics.lifetime)).scalar()
    churn_rate = db.session.query(func.sum(SalesMetrics.churn)).scalar()
    sroi = db.session.query(func.sum(SalesMetrics.s_roi)).scalar()

    total_sales_revenue = total_sales_revenue
    average_conversion_rate = conversion_rates/total_id
    total_cac = cac
    average_clv = clv/total_id
    average_churn_rate = churn_rate/total_id
    average_roi = sroi/total_id
    send_mail("Vishnuraj", "gdscsnscollegeofengineering@gmail.com","Sales report","Sales Data of your organization\n\n"+'Total Sales Revenue : '+str(total_sales_revenue)+'\nAverage Conversion Rate : '+str(average_conversion_rate)+'\nTotal CAC : '+str(total_cac)+'\nAverage CLV : '+str(average_clv)+'\nAverage Churn Rate : '+str(average_churn_rate)+'\nAverage ROI : '+str(average_roi))
    if current_user.role == "CEO":
        return render_template("ceo/get_sales.html",
                            data=data,
                            total_sales_revenue=total_sales_revenue,
                            average_conversion_rate=average_conversion_rate,
                            total_cac=total_cac,
                            average_clv=average_clv,
                            average_churn_rate=average_churn_rate,
                            average_roi=average_roi)
    
    elif current_user.role == "Manager":
        return render_template("manager/get_sales.html",
                            data=data,
                            total_sales_revenue=total_sales_revenue,
                            average_conversion_rate=average_conversion_rate,
                            total_cac=total_cac,
                            average_clv=average_clv,
                            average_churn_rate=average_churn_rate,
                            average_roi=average_roi)
    else:
        return "Invalid request method"
    

def for_visual():
    # total_entries = db.session.filterby(id).count()
    total_production_output = db.session.query(func.sum(OperationalMetrics.total_production_output)).scalar()
    downtime_percentage = db.session.query(func.sum(OperationalMetrics.downtime_percentage)).scalar()
    supplier_performance = db.session.query(func.sum(OperationalMetrics.supplier_performance)).scalar()

    
    total_production_output = round(total_production_output,2)/10000
    downtime_percentage=(round(downtime_percentage,2))
    supplier_performance=round(supplier_performance,2)

    return total_production_output,downtime_percentage,supplier_performance


def for_charts():
    total_revenue = db.session.query(func.sum(FinancialMetrics.revenue)).scalar()
    total_expenses = db.session.query(func.sum(FinancialMetrics.expenses)).scalar()
    total_profit = db.session.query(func.sum(FinancialMetrics.profit)).scalar()
    
    gross_profit = round((total_profit / total_revenue) * 100,2)
    net_profit = round((total_profit / total_revenue) * 100,2)
    current_ratio = round(total_revenue / total_expenses,2)
    quick_ratio = round(current_ratio,2)
    debt_equity = round(total_expenses/total_revenue,2)
    debt_asset = round(total_expenses/total_profit,2)

    return gross_profit, net_profit, current_ratio, quick_ratio, debt_equity, debt_asset


def for_dashboard():

    total_id = db.session.query(func.sum(SalesMetrics.id)).scalar()
    total_sales_revenue = db.session.query(func.sum(SalesMetrics.sales_revenue)).scalar()
    conversion_rates = db.session.query(func.sum(SalesMetrics.conversion)).scalar()
    cac = db.session.query(func.sum(SalesMetrics.acquisition)).scalar()
    clv = db.session.query(func.sum(SalesMetrics.lifetime)).scalar()
    churn_rate = db.session.query(func.sum(SalesMetrics.churn)).scalar()
    sroi = db.session.query(func.sum(SalesMetrics.s_roi)).scalar()

    total_sales_revenue = round(total_sales_revenue,2)
    average_conversion_rate = round(conversion_rates/total_id,2)
    total_cac = round(cac,2)
    average_clv = round(clv/total_id,2)
    average_churn_rate = round(churn_rate/total_id,2)
    average_roi = round(sroi/total_id, 2)

    return total_sales_revenue,average_conversion_rate,total_cac,average_clv,average_churn_rate,average_roi


def for_kaggle():

    sum_M01AB = db.session.query(func.sum(KaggleData.M01AB)).scalar()
    sum_M01AE = db.session.query(func.sum(KaggleData.M01AE)).scalar()
    sum_N02BA = db.session.query(func.sum(KaggleData.N02BA)).scalar()
    sum_N02BE = db.session.query(func.sum(KaggleData.N02BE)).scalar()
    sum_N05B = db.session.query(func.sum(KaggleData.N05B)).scalar()
    sum_N05C = db.session.query(func.sum(KaggleData.N05C)).scalar()
    sum_R03 = db.session.query(func.sum(KaggleData.R03)).scalar()
    sum_R06 = db.session.query(func.sum(KaggleData.R06)).scalar()
    total_sum = db.session.query(func.sum(KaggleData.id)).scalar()

    M01AB = sum_M01AB/total_sum * 1000
    M01AE = sum_M01AE/total_sum * 1000
    N02BA = sum_N02BA/total_sum * 1000
    N02BE = sum_N02BE/total_sum * 1000
    N05B = sum_N05B/total_sum * 1000
    N05C = sum_N05C/total_sum * 1000
    R03 = sum_R03/total_sum * 1000
    R06 = sum_R06/total_sum * 1000
    
    return M01AB,M01AE,N02BA,N02BE-20,N05B,N05C,R03,R06

# Dashboard

@blueprint.route('/ceo/dashboard')
@login_required  # Ensure that only authenticated users can access this route
def ceo_dashboard():
    sales = SalesMetrics.query.all()
    finance = FinancialMetrics.query.all()
    operation = OperationalMetrics.query.all()
    task = Tasks.query.all()
    notify = Notification.query.all()
    if current_user.is_authenticated and current_user.role == 'CEO':
        total_sales = for_dashboard()
        financial_metrics = for_charts()
        operational_data = for_visual()
        kaggle_data = for_kaggle()
       
        result_sales = list(total_sales)
        result_financial = list(financial_metrics)
        result_operation = list(operational_data)
        result_kaggle = list(kaggle_data)
  
        return render_template('ceo/index.html',
                task = task,
                notify = notify,
                total_sale=total_sales,
                avg_churn=result_sales[4],
                avg_roi = result_sales[5],
                debt_asset = result_financial[5],
                debt_equity = result_financial[4],
                financial_metrics=financial_metrics,
                operational_data=operational_data,
                downtime = result_operation[1],
                total_output = result_operation[0],
                M01AB=result_kaggle[0],
                M01AE=result_kaggle[1],
                N02BA=result_kaggle[2],
                N02BE=result_kaggle[3],
                N05B=result_kaggle[4],
                N05C=result_kaggle[5],
                R03=result_kaggle[6],
                R06=result_kaggle[7]
                )
    else:
        return render_template('error.html', error_msg='Access Denied: You must be a CEO to access this page')


@blueprint.route('/manager/dashboard')
@login_required  # Ensure that only authenticated users can access this route
def manager_dashboard():
    sales = SalesMetrics.query.all()
    finance = FinancialMetrics.query.all()
    operation = OperationalMetrics.query.all()
    notify = Notification.query.all()
    if current_user.is_authenticated and current_user.role == 'Manager':
        total_sales = for_dashboard()
        financial_metrics = for_charts()
        operational_data = for_visual()
        kaggle_data = for_kaggle()
       
        result_sales = list(total_sales)
        result_financial = list(financial_metrics)
        result_operation = list(operational_data)
        result_kaggle = list(kaggle_data)

        return render_template('manager/index.html',
                notify=notify,
                total_sale=total_sales,
                avg_churn=result_sales[4],
                avg_roi = result_sales[5],
                debt_asset = result_financial[5],
                debt_equity = result_financial[4],
                total_production = result_operation[0],
                financial_metrics=financial_metrics,
                operational_data=operational_data,
                downtime = result_operation[1],
                total_output = result_operation[0],
                M01AB=result_kaggle[0],
                M01AE=result_kaggle[1],
                N02BA=result_kaggle[2],
                N02BE=result_kaggle[3],
                N05B=result_kaggle[4],
                N05C=result_kaggle[5],
                R03=result_kaggle[6],
                R06=result_kaggle[7]
                )
    else:
        return render_template('error.html', error_msg='Access Denied: You must be a Manager to access this page')


@blueprint.route('/employee/dashboard')
@login_required  # Ensure that only authenticated users can access this route
def employee_dashboard():
    task = Tasks.query.all()
    if current_user.department == "Sales":
        user = Users.query.filter_by(role="Manager").filter_by(department="Sales").first()
    elif current_user.department == "Finance":
        user = Users.query.filter_by(role="Manager").filter_by(department="Finance").first()
    elif current_user.department == "Operational":
        user = Users.query.filter_by(role="Manager").filter_by(department="Operational").first()
    # Check if the user is authenticated and has the "employee" role
    if current_user.is_authenticated and current_user.role == 'Employee':
        return render_template("employee/index.html", task=task, id=user.id, email=user.email, name = user.username, phone = user.phone)
    else:
        # If the user is not authenticated or doesn't have the "ceo" role, redirect them to a different page or show an error message
        return render_template('error.html', error_msg='Access Denied: You must be a Employee to access this page')


#chat message

@blueprint.route('/messages', methods=['POST', 'GET'])
@login_required
def messages():
    if request.method == 'POST':
        # This is a POST request, so it's for sending a message
        message = request.form.get('message')
        if message:
            chat_message = ChatMessages(username=current_user.username, message=message)
            db.session.add(chat_message)
            db.session.commit()
            return jsonify({'status': 'Message sent successfully'})
        else:
            return jsonify({'status': 'Invalid request'})
        
    elif request.method == 'GET':
        # This is a GET request, so it's for retrieving messages
        chat = ChatMessages.query.all()

        if current_user.role == "CEO":
            return render_template('ceo/chat_message.html', data=chat)
        elif current_user.role == "Manager":
            return render_template('manager/chat_room.html', data=chat)
        else:
            return "Invalid request method"
    else:
        return "Invalid request method"
    

# employee message

@blueprint.route('/message_operational', methods=['POST', 'GET'])
@login_required
def message_operational():
    if request.method == 'POST':
        # This is a POST request, so it's for sending a message
        message = request.form.get('message')
        if message:
            chat_message = OperationalChat(username=current_user.username, message=message)
            db.session.add(chat_message)
            db.session.commit()
            return jsonify({'status': 'Message sent successfully'})
        else:
            return jsonify({'status': 'Invalid request'})
        
    elif request.method == 'GET':
        # This is a GET request, so it's for retrieving messages
        chat = OperationalChat.query.all()

        if current_user.role == "Manager":
            return render_template('manager/chat_message.html', data=chat)
        elif current_user.role == "Employee":
            return render_template('employee/chat_message.html', data=chat)
        else:
            return "Invalid request method"
    else:
        return "Invalid request method"
    

@blueprint.route('/message_sales', methods=['POST', 'GET'])
@login_required
def message_sales():
    if request.method == 'POST':
        # This is a POST request, so it's for sending a message
        message = request.form.get('message')
        if message:
            chat_message = SalesChat(username=current_user.username, message=message)
            db.session.add(chat_message)
            db.session.commit()
            return jsonify({'status': 'Message sent successfully'})
        else:
            return jsonify({'status': 'Invalid request'})
        
    elif request.method == 'GET':
        # This is a GET request, so it's for retrieving messages
        chat = SalesChat.query.all()

        if current_user.role == "Manager":
            return render_template('manager/chat_sales.html', data=chat)
        elif current_user.role == "Employee":
            return render_template('employee/chat_sales.html', data=chat)
        else:
            return "Invalid request method"
    else:
        return "Invalid request method"
    


@blueprint.route('/message_finance', methods=['POST', 'GET'])
@login_required
def message_finance():
    if request.method == 'POST':
        # This is a POST request, so it's for sending a message
        message = request.form.get('message')
        if message:
            chat_message = FinanceChat(username=current_user.username, message=message)
            db.session.add(chat_message)
            db.session.commit()
            return jsonify({'status': 'Message sent successfully'})
        else:
            return jsonify({'status': 'Invalid request'})
        
    elif request.method == 'GET':
        # This is a GET request, so it's for retrieving messages
        chat = FinanceChat.query.all()

        if current_user.role == "Manager":
            return render_template('manager/chat_finance.html', data=chat)
        elif current_user.role == "Employee":
            return render_template('employee/chat_finance.html', data=chat)
        else:
            return "Invalid request method"
    else:
        return "Invalid request method"
    

# Notification

@blueprint.route('/notify')
@login_required
def notify():
    data = Notification.query.all()
    mail_mess = Notification.query.order_by(Notification.id.desc()).first()
    name = mail_mess.username
    message = mail_mess.message
    send_mail("Vishnuraj","gdscsnscollegeofengineering@gmail.com", 'Notifications from your organization', 'Notification\n\n'+'Name : '+name+"\n\nMessage : "+message)
    if current_user.role == 'CEO':
        return render_template('ceo/notifications.html', data=data)
    elif current_user.role == 'Manager':
        return render_template('manager/notifications.html', data=data)
    elif current_user.role == "Employee":
        return render_template('employee/notifications.html', data=data)


# delete messages

@blueprint.route('/delete_all_messages')
def delete_message():
    # Find the message by its ID
    message = ChatMessages.query.all()
    if message:
        db.session.query(ChatMessages).delete()
        db.session.commit()
        return "Message deleted successfully"
    else:
        return "Message not found", 404

@blueprint.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    data = FinancialMetrics.query.get(id)
    if data:
        db.session.delete(data)
        db.session.commit()
        return "Message deleted successfully"
    else:
        return "Message not found", 404

@blueprint.route('/remove/<int:id>', methods=['POST'])
@login_required
def remove(id):
    data = OperationalMetrics.query.get(id)
    if data:
        db.session.delete(data)
        db.session.commit()
        return "Message deleted successfully"
    else:
        return "Message not found", 404

@blueprint.route('/empty/<int:id>', methods=['POST'])
@login_required
def empty(id):
    data = SalesMetrics.query.get(id)
    if data:
        db.session.delete(data)
        db.session.commit()
        return "Message deleted successfully"
    else:
        return "Message not found", 404
    

# delete tasks
@blueprint.route('/task_delete/<int:id>', methods=['POST'])
@login_required
def task_delete(id):
    data = Tasks.query.get(id)
    if data:
        db.session.delete(data)
        db.session.commit()
        return "Message deleted successfully"
    else:
        return "Message not found", 404

# delete manager Task
@blueprint.route('/manager_task_delete/<int:id>', methods=['POST'])
@login_required
def manager_task_delete(id):
    data = AssignTask.query.get(id)
    if data:
        db.session.delete(data)
        db.session.commit()
        return "Message deleted successfully"
    else:
        return "Message not found", 404

# profile

@blueprint.route('/profile')
@login_required
def profile():
    data = Users.query.all()
    if current_user.role == "CEO":
        return render_template('ceo/profile.html',data=data)
    elif current_user.role == "Manager":
        return render_template('manager/profile.html',data=data)
    elif current_user.role == "Employee":
        return render_template('employee/profile.html',data=data)


# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500

# kaggle data set

def kaggle():
    csv_file = '/Users/vishnurajsaravanan/Desktop/CEO/flask-material-dashboard/apps/data/sales/salesdaily.csv'
    data = pd.read_csv(csv_file)

    for index, row in data.iterrows():
        record = KaggleData(
            M01AB=row['M01AB'],
            M01AE=row['M01AE'],
            N02BA=row['N02BA'],
            N02BE=row['N02BE'],
            N05B=row['N05B'],
            N05C=row['N05C'],
            R03=row['R03'],
            R06=row['R06'],
            Year=row['Year'],
            Month=row['Month'],
            Hour=row['Hour'],
            Weekday=row['Weekday Name']
        )
        db.session.add(record)

    # Commit the changes
    db.session.commit()

    # Close the session
    db.session.close()
