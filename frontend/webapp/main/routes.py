#****************************************************************************
#    Application:   Anerkennung AI Cockpit
#    Module:        frontend.webapp.main.routes
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.1
#****************************************************************************

#=== Imports

from flask import render_template, request, current_app
from flask_login import login_required, current_user

from werkzeug.utils import secure_filename
import os

from frontend.webapp.main import main_bp

#=== Helper functions

def _allowed_file(filename: str) -> bool:
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
    )


#=== Routes
@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Main dashboard route.
    Shows different sections depending on the user's role.
    Roles:
        - admin
        - recruiter
        - candidate
    """
    return render_template("dashboard.html")