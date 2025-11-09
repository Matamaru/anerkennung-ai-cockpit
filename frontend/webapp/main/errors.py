#****************************************************************************
#    Application:   Anerkennung AI Cockpit
#    Module:        frontend.webapp.main.errors
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.1
#****************************************************************************

#=== Imports

from flask import render_template
from frontend.webapp.main import main_bp

#=== Error Handlers
@main_bp.app_errorhandler(404)
def not_found_error(error):
    return render_template("error.html", code=404, message="Page not found."), 404

@main_bp.app_errorhandler(413)
def too_large_error(error):
    return render_template("error.html", code=413, message="Upload too large. Reduce file size or count."), 413

@main_bp.app_errorhandler(500)
def internal_error(error):
    return render_template("error.html", code=500, message="Unexpected server error."), 500
