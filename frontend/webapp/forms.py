from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

class loginForm(FlaskForm):
    # TODO Replace with Flask-Login forms
    # TODO ADD validators
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    # TODO Replace with Flask-Login forms
    # TODO ADD validators
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    role_name = SelectField('Role', choices=[('admin', 'Admin'), ('recruiter', 'Recruiter'), ('candidate', 'Candidate')], default='candidate', validators=[DataRequired()])
    submit = SubmitField('Save')

class RequirementForm(FlaskForm):
    country_name = StringField('Country Name', validators=[DataRequired()])
    state_name = StringField('State Name')
    req_name = StringField('Requirement Name', validators=[DataRequired()])
    description = StringField('Description')
    optional = SelectField('Optional', choices=[('true', 'Yes'), ('false', 'No')], default='false', validators=[DataRequired()])
    translation_required = SelectField('Translation Required', choices=[('true', 'Yes'), ('false', 'No')], default='false', validators=[DataRequired()])
    fullfilled = SelectField('Fulfilled', choices=[('true', 'Yes'), ('false', 'No')], default='false', validators=[DataRequired()])
    submit = SubmitField('Save')
