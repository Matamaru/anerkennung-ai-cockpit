#****************************************************************************
#    Application:   Anerkennung AI Cockpit
#    Module:        frontend.webapp.admin.__init__
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.1
#****************************************************************************

#=== Imports

from flask import Blueprint
admin_bp = Blueprint("admin", __name__, url_prefix="")
