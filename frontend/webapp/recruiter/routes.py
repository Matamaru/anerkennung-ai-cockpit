#****************************************************************************
#    Application:   Anerkennung AI Cockpit
#    Module:        frontend.webapp.recruiter.routes
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.1
#****************************************************************************

#=== Imports
from flask import render_template, request
from flask_login import login_required
from frontend.webapp.recruiter import recruiter_bp
from frontend.webapp.utils import recruiter_required
from backend.datamodule.sa import session_scope
from backend.datamodule.orm import Application as ApplicationORM, Role as RoleORM, User as UserORM
from sqlalchemy import func

#=== Routes
@login_required
@recruiter_required
@recruiter_bp.route("/dashboard/recruiter/candidate-management")
def candidate_management():
    search = (request.args.get("q") or "").strip().lower()
    with session_scope() as session:
        rows = (
            session.query(
                UserORM.user_id,
                UserORM.username,
                UserORM.email,
                func.count(ApplicationORM.id).label("application_count"),
            )
            .join(RoleORM, UserORM.role_id == RoleORM.role_id)
            .outerjoin(ApplicationORM, ApplicationORM.user_id == UserORM.user_id)
            .filter(RoleORM.role_name == "candidate")
            .group_by(UserORM.user_id, UserORM.username, UserORM.email)
            .order_by(UserORM.username.asc())
            .all()
        )

    candidates = []
    for row in rows:
        if search and search not in (row.username or "").lower() and search not in (row.email or "").lower():
            continue
        candidates.append(
            {
                "user_id": row.user_id,
                "username": row.username,
                "email": row.email,
                "application_count": row.application_count,
            }
        )

    return render_template("recruiter_candidatemanagement.html", candidates=candidates, query=search)

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
