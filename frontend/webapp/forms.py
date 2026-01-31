from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

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
    profession_name = StringField('Profession Name', validators=[DataRequired()])
    country_name = StringField('Country Name', validators=[DataRequired()])
    state_name = StringField('State Name')
    req_name = StringField('Requirement Name', validators=[DataRequired()])
    description = StringField('Description')
    optional = SelectField('Optional', choices=[('true', 'Yes'), ('false', 'No')], default='false', validators=[DataRequired()])
    translation_required = SelectField('Translation Required', choices=[('true', 'Yes'), ('false', 'No')], default='false', validators=[DataRequired()])
    fullfilled = SelectField('Fulfilled', choices=[('true', 'Yes'), ('false', 'No')], default='false', validators=[DataRequired()])
    allow_multiple = SelectField('Allow Multiple Uploads', choices=[('true', 'Multiple'), ('false', 'Unique')], default='true', validators=[DataRequired()])
    submit = SubmitField('Save')

class DocumentTypeForm(FlaskForm):
    name = StringField(
        "Document Type Name",
        validators=[DataRequired(), Length(max=255)]
    )
    description = TextAreaField(
        "Description",
        validators=[Length(max=2000)]
    )
    submit = SubmitField("Save")

class StateForm(FlaskForm):
    country_name = StringField('Country Name', validators=[DataRequired()])
    name = StringField('State Name', validators=[DataRequired()])
    abbreviation = StringField('Abbreviation', validators=[DataRequired()])
    description = StringField('Description')
    submit = SubmitField('Save')

class CountryForm(FlaskForm):
    name = StringField('Country Name', validators=[DataRequired()])
    code = StringField('Country Code', validators=[DataRequired(), Length(min=2, max=2)])
    description = StringField('Description')
    submit = SubmitField('Save')
