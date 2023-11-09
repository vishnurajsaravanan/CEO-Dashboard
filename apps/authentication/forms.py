# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField
from wtforms.validators import Email, DataRequired, Length, Optional

# login and registration

class LoginForm(FlaskForm):
    username = StringField('Username',
                         id='username_login',
                         validators=[DataRequired()])
    password = PasswordField('Password',
                             id='pwd_login',
                             validators=[DataRequired()])
    role = SelectField('Role', choices=[('', 'Select Role'), ('CEO', 'CEO'), ('Manager', 'Manager'), ('Employee', 'Employee')],
                       id='roles',
                       default='', 
                       validators=[DataRequired()])
    department = SelectField('Department',
                            choices=[('', 'Select Department'), ('Sales', 'Sales'), ('Finance', 'Finance'), ('Operational', 'Operational')],
                            id='department',
                            default="",
                            validators=[Optional()])

    def validate_department(self, field):
        # Check if the department is required when role is Employee or Manager
        if (self.role.data == 'Employee' or self.role.data == 'Manager') and not field.data:
            raise ValueError('Department is required for Employees and Managers.')


class CreateAccountForm(FlaskForm):
    username = StringField('Username',
                         id='username_create',
                         validators=[DataRequired()])
    phone = IntegerField('Phone',
                      id='phone_create',
                      validators=[DataRequired()])
    email = StringField('Email',
                      id='email_create',
                      validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             id='pwd_create',
                             validators=[DataRequired()])
    role = SelectField('Role', choices=[('', 'Select Role'), ('CEO', 'CEO'), ('Manager', 'Manager'), ('Employee', 'Employee')],
                       id='roles',
                       default='', 
                       validators=[DataRequired()])
    department = SelectField('Department',
                            choices=[('', 'Select Department'), ('Sales', 'Sales'), ('Finance', 'Finance'), ('Operational', 'Operational')],
                            id='department',
                            default="",
                            validators=[Optional()])

    def validate_department(self, field):
        # Check if the department is required when role is Employee or Manager
        if (self.role.data == 'Employee' or self.role.data == 'Manager') and not field.data:
            raise ValueError('Department is required for Employees and Managers.')
