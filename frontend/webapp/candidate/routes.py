#****************************************************************************
#    Application:   Anerkennung AI Cockpit
#    Module:        frontend.webapp.candidate.routes
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.3
#****************************************************************************

#=== Imports
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from frontend.webapp.candidate import candidate_bp
from frontend.webapp.utils import candidate_required
from backend.datamodule.models.profession import Profession
from backend.datamodule.models.country import Country
from backend.datamodule.models.state import State 
from backend.datamodule.models.application import Application


#=== helpers

def _load_select_data():
    professions_tuple = Profession.get_all()
    professions = [Profession.from_tuple(p) for p in professions_tuple] if professions_tuple else []
    countries_tuple = Country.get_all()
    countries = [Country.from_tuple(c) for c in countries_tuple] if countries_tuple else []
    states_tuple = State.get_all()
    states = [State.from_tuple(s) for s in states_tuple] if states_tuple else []
    return professions, countries, states

def _attach_display_data(applications, professions, countries, states):
    """
    Attach profession_name, country_name, state_name to each Application object.
    """

    prof_map = {p.id: p.name for p in professions}
    country_map = {c.id: c.name for c in countries}
    state_map = {s.id: s.name for s in states}

    for a in applications:
        # IDs -> names
        a.profession_name = prof_map.get(a.profession_id)
        a.country_name = country_map.get(a.country_id)
        a.state_name = state_map.get(a.state_id)

    return applications


#=== Routes

@login_required
@candidate_required
@candidate_bp.route("/dashboard/candidate/documentmanagement")
def document_management():
    user_id = current_user.id
    selected_app_id = request.args.get("application_id")

    app_tuple = Application.get_by_user_id(user_id)
    applications = [Application.from_tuple(a) for a in app_tuple] if app_tuple else []

    return render_template(
        "candidate_documentmanagement.html",
        applications=applications,
        selected_application_id=selected_app_id,
    )


@login_required
@candidate_required
@candidate_bp.route("/dashboard/candidate/applicationmanagement")
def applications_management():
    """
    List view + right side empty (info alert).
    """
    user_id = current_user.id

    app_tuple = Application.get_by_user_id(user_id)
    applications = [Application.from_tuple(a) for a in app_tuple] if app_tuple else []

    professions, countries, states = _load_select_data()

    applications = _attach_display_data(applications, professions, countries, states)

    return render_template(
        "candidate_applicationsmanagement.html",
        applications=applications,
        application=None,
        professions=professions,
        countries=countries,
        states=states,
        is_new=False,
    )


@login_required
@candidate_required
@candidate_bp.route("/dashboard/candidate/applicationmanagement/new")
def applicationsmanagement_new():
    """
    Same page, but right side shows an empty 'New application' form.
    """
    user_id = current_user.id

    app_tuple = Application.get_by_user_id(user_id)
    applications = [Application.from_tuple(a) for a in app_tuple] if app_tuple else []

    professions, countries, states = _load_select_data()

    applications = _attach_display_data(applications, professions, countries, states)

    return render_template(
        "candidate_applicationsmanagement.html",
        applications=applications,
        application=None,
        professions=professions,
        countries=countries,
        states=states,
        is_new=True,
    )


@login_required
@candidate_required
@candidate_bp.route("/dashboard/candidate/applicationmanagement/<app_id>")
def applicationsmanagement_detail(app_id):
    """
    Same page, but right side shows details for one existing application.
    """
    user_id = current_user.id

    # list for left side
    app_tuple = Application.get_by_user_id(user_id)
    applications = [Application.from_tuple(a) for a in app_tuple] if app_tuple else []

    # single application for right side
    row = Application.get_by_id(app_id)
    application = Application.from_tuple(row) if row else None

    professions, countries, states = _load_select_data()

    applications = _attach_display_data(applications, professions, countries, states)

    return render_template(
        "candidate_applicationsmanagement.html",
        applications=applications,
        application=application,
        professions=professions,
        countries=countries,
        states=states,
        is_new=False,
    )


@login_required
@candidate_required
@candidate_bp.route(
    "/dashboard/candidate/applicationmanagement/save",
    methods=["POST"]
)
def applicationsmanagement_save():
    """
    Save new or existing application.
    """
    user_id      = current_user.id
    app_id       = request.form.get("id")
    profession_id = request.form.get("profession_id")
    country_id    = request.form.get("country_id")
    state_id      = request.form.get("state_id")

    if app_id:
        update_app_tuple = Application.get_by_id(app_id)
        update_app = Application.from_tuple(update_app_tuple)
        values = (
            user_id,
            profession_id,
            country_id,
            state_id,
            app_id
        )
        update_app.update(values)
        selected_id = app_id
    else:
        new_application = Application(
            user_id=user_id,
            profession_id=profession_id,
            country_id=country_id,
            state_id=state_id,
        )
        new_app_tuple = new_application.insert()
        selected_id = new_app_tuple[0] if new_app_tuple else None   

    return redirect(url_for("candidate.applicationsmanagement_detail", app_id=selected_id))


@login_required
@candidate_required
@candidate_bp.route(
    "/dashboard/candidate/applicationmanagement/<app_id>/delete",
    methods=["POST"]
)
def applicationsmanagement_delete(app_id):
    """
    Delete existing application.
    """
    delete_app_tuple = Application.get_by_id(app_id)
    delete_app = Application.from_tuple(delete_app_tuple)
    result = delete_app.delete()
    if result:
        # flash success message
        flash(f"Application {app_id} deleted successfully.")
    else:
        flash(f"Application {app_id} could not be deleted.")
    return redirect(url_for("candidate.applicationsmanagement_new"))


@login_required
@candidate_required
@candidate_bp.route("/dashboard/candidate/contact-recruiter")
def contact_recruiter():
    return render_template("candidate_contactrecruiter.html")
