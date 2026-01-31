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
from backend.datamodule.models.profession import Profession
from backend.datamodule.models.country import Country
from backend.datamodule.models.state import State
from sqlalchemy import func

#=== Routes
@login_required
@recruiter_required
@recruiter_bp.route("/dashboard/recruiter/candidate-management")
def candidate_management():
    search = (request.args.get("q") or "").strip().lower()
    selected_user_id = request.args.get("user_id")
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
        selected_user = None
        applications = []
        if selected_user_id:
            selected_user = session.query(UserORM).filter_by(user_id=selected_user_id).first()
            applications = (
                session.query(
                    ApplicationORM.id,
                    ApplicationORM.profession_id,
                    ApplicationORM.country_id,
                    ApplicationORM.state_id,
                    ApplicationORM.time_created,
                )
                .filter(ApplicationORM.user_id == selected_user_id)
                .order_by(ApplicationORM.time_created.desc())
                .all()
            )

    profession_map = {p.id: p.name for p in (Profession.from_tuple(r) for r in (Profession.get_all() or []))}
    country_map = {c.id: c.name for c in (Country.from_tuple(r) for r in (Country.get_all() or []))}
    state_map = {s.id: s.name for s in (State.from_tuple(r) for r in (State.get_all() or []))}
    applications_view = []
    for app in applications:
        applications_view.append(
            {
                "id": app.id,
                "profession_name": profession_map.get(app.profession_id, app.profession_id),
                "country_name": country_map.get(app.country_id, app.country_id),
                "state_name": state_map.get(app.state_id, app.state_id),
                "time_created": app.time_created,
            }
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

    return render_template(
        "recruiter_candidatemanagement.html",
        candidates=candidates,
        query=search,
        selected_user=selected_user,
        applications=applications_view,
    )

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
