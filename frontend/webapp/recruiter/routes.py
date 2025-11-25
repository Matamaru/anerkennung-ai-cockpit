#****************************************************************************
#    Application:   Anerkennung AI Cockpit
#    Module:        frontend.webapp.recruiter.routes
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.1
#****************************************************************************

#=== Imports
from flask import render_template
from flask_login import login_required
from frontend.webapp.recruiter import recruiter_bp
from frontend.webapp.utils import recruiter_required

#=== Routes
@login_required
@recruiter_required
@recruiter_bp.route("/dashboard/recruiter/candidate-management")
def candidate_management():
    return render_template("recruiter_candidatemanagement.html")

@login_required
@recruiter_required
@recruiter_bp.route("/dashboard/recruiter/contact-recruiters")
def contact_recruiters():
    return render_template("recruiter_contactrecruiters.html")

@login_required
@recruiter_required
@recruiter_bp.route("/dashboard/recruiter/contact-admin")
def contact_admin():
    return render_template("recruiter_contactadmin.html")