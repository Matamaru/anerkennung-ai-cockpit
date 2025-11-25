#****************************************************************************
#    Application:   Anerkennung AI Cockpit
#    Module:        frontend.webapp.candidate.routes
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.1
#****************************************************************************

#=== Imports
from flask import render_template
from flask_login import login_required
from frontend.webapp.candidate import candidate_bp
from frontend.webapp.utils import candidate_required    

#=== Routes
@login_required
@candidate_required
@candidate_bp.route("/dashboard/candidate/documentmanagement")
def document_management():
    return render_template("candidate_documentmanagement.html")

@login_required
@candidate_required
@candidate_bp.route("/dashboard/candidate/applicationmanagement")
def applications_management():
    return render_template("candidate_applicationmanagement.html")

@login_required
@candidate_required
@candidate_bp.route("/dashboard/candidate/contact-recruiter")
def contact_recruiter():
    return render_template("candidate_contactrecruiter.html")
  

