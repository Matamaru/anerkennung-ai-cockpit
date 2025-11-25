from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    role_name = SelectField('Role', choices=[('admin', 'Admin'), ('recruiter', 'Recruiter'), ('candidate', 'Candidate')], default='candidate', validators=[DataRequired()])
    submit = SubmitField('Save')
