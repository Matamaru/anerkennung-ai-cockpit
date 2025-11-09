#****************************************************************************
#    Application:   Anerkennung AI Cockpit
#    Module:        frontend.webapp.auth.routes
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.1
#****************************************************************************

#=== Imports

from flask import render_template, request, jsonify, url_for
from . import auth_bp

# --- Login modal (used inside any page)
@auth_bp.get("/login")
def login_page():
    # This returns just the modal HTML for inclusion or dynamic fetch
    return render_template("auth/login_modal.html")

@auth_bp.post("/login")
def login_submit():
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    # TODO: replace with real auth + sessions (Flask-Login or your own)
    if username == "admin" and password == "1234":
        return jsonify({"success": True, "redirect": url_for("main.index")})
    return jsonify({"success": False, "message": "Invalid credentials"})
