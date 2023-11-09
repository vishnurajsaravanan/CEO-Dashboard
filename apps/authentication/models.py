# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import datetime
from flask_login import UserMixin
import pytz

from apps import db, login_manager

from apps.authentication.util import hash_pass


class Users(db.Model, UserMixin):

    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=False)
    phone = db.Column(db.Integer,unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary(10))
    role = db.Column(db.String(10))
    department = db.Column(db.String(64), default=None)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)

# class for storing financial data
class FinancialMetrics(db.Model):
    __tablename__ = 'financial_metrics'
    id = db.Column(db.Integer, primary_key=True)
    revenue = db.Column(db.Float, nullable=False)
    profit = db.Column(db.Float, nullable=False)
    expenses = db.Column(db.Float, nullable=False)

    def __init__(self, revenue, profit, expenses):
        self.revenue = revenue
        self.profit = profit
        self.expenses = expenses

# sales data

class SalesMetrics(db.Model):
    __tablename__ = 'sales_metrics'
    
    
    id = db.Column(db.Integer, primary_key=True)
    # username = db.Column(db.String(64), unique=False)
    sales_revenue = db.Column(db.Float, nullable=False)
    conversion = db.Column(db.Float, nullable=False)
    acquisition = db.Column(db.Float, nullable=False)
    lifetime = db.Column(db.Float, nullable=False)
    churn = db.Column(db.Float, nullable=False)
    s_roi = db.Column(db.Float, nullable=False)


    def __init__(self, sales_revenue, conversion, acquisition, lifetime, churn, s_roi):
        # self.username = username
        self.sales_revenue = sales_revenue
        self.conversion = conversion
        self.acquisition = acquisition
        self.lifetime = lifetime
        self.churn = churn
        self.s_roi = s_roi

# operational data

class OperationalMetrics(db.Model):

    __tablename__ = 'operational_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    total_production_output = db.Column(db.Float, nullable=False)
    downtime_percentage = db.Column(db.Float, nullable=False)
    supplier_performance = db.Column(db.Float, nullable=False)

    def __init__(self, total_production_output, downtime_percentage,supplier_performance):
        self.total_production_output = total_production_output
        self.downtime_percentage = downtime_percentage
        self.supplier_performance = supplier_performance

# class for csv file

class KaggleData(db.Model):
    
    __tablename__ = 'kaggle_dataset'

    id = db.Column(db.Integer, primary_key=True)
    M01AB = db.Column(db.Float, nullable=False)
    M01AE = db.Column(db.Float, nullable=False)
    N02BA = db.Column(db.Float, nullable=False)
    N02BE = db.Column(db.Float, nullable=False)
    N05B = db.Column(db.Float, nullable=False)
    N05C = db.Column(db.Float, nullable=False)
    R03 = db.Column(db.Float, nullable=False)
    R06 = db.Column(db.Float, nullable=False)
    Year = db.Column(db.Integer, nullable=False)
    Month = db.Column(db.String(255), nullable=False)
    Hour = db.Column(db.Integer, nullable=False)
    Weekday = db.Column(db.String(255), nullable=False)
    
    
    def __init__(self, M01AB,M01AE,	N02BA,N02BE,N05B,N05C,R03,R06,Year,Month,Hour,Weekday):
        self.M01AE = M01AE
        self.N02BA = N02BA
        self.M01AB = M01AB
        self.N02BE = N02BE
        self.N05B = N05B
        self.N05C = N05C
        self.R03 = R03
        self.R06 = R06
        self.Year = Year
        self.Month = Month
        self.Hour = Hour
        self.Weekday = Weekday


# chat table

class ChatMessages(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(255), nullable=False)


    def __init__(self, username, message):
        self.username = username
        self.message = message


class OperationalChat(db.Model):
    __tablename__ = 'operational_chat'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(255), nullable=False)


    def __init__(self, username, message):
        self.username = username
        self.message = message


class SalesChat(db.Model):
    __tablename__ = 'sales_chat'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(255), nullable=False)


    def __init__(self, username, message):
        self.username = username
        self.message = message

class FinanceChat(db.Model):
    __tablename__ = 'finance_chat'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(255), nullable=False)


    def __init__(self, username, message):
        self.username = username
        self.message = message





# tasks table

class Tasks(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    task = db.Column(db.String(255), nullable=False)
    is_checked = db.Column(db.Boolean, default=False)

    def __init__(self, username, task, is_checked):
        self.username = username
        self.task = task
        self.is_checked = is_checked

class AssignTask(db.Model):
    __tablename__ = 'assign_task'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    task = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(255), nullable=False)
    is_checked = db.Column(db.Boolean, default=False)

    def __init__(self, username, task, department, is_checked):
        self.username = username
        self.task = task
        self.department = department
        self.is_checked = is_checked


# Notification data

class Notification(db.Model):

    __tablename__ = 'notification'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    message = db.Column(db.String(230), nullable=False)

    def __init__(self, username, message):
        self.username = username
        self.message = message




@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None
