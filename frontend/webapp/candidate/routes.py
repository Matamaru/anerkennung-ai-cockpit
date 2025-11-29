#****************************************************************************
#    Application:   Anerkennung AI Cockpit
#    Module:        frontend.webapp.candidate.routes
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.3
#****************************************************************************

#=== Imports
from uuid import uuid4
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from backend.datamodule.models.document import Document
from frontend.webapp.candidate import candidate_bp
from frontend.webapp.utils import candidate_required
from backend.datamodule.models.profession import Profession
from backend.datamodule.models.country import Country
from backend.datamodule.models.state import State 
from backend.datamodule.models.application import Application
from backend.datamodule import db


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

def get_documents_for_application(application_id) -> list[Document]:
    """Fetch all documents linked to a given application ID."""
    query = """
    SELECT 
        ad.id AS app_doc_id,
        ad.application_id,
        d.id AS document_id,
        d.file_id,
        dt.name AS document_type_name,
        f.filename,
        f.filepath,
        doc_data.ocr_full_text,
        d.status_id,
        ad.requirements_id
    FROM _app_docs ad
    JOIN _documents d ON ad.document_id = d.id
    JOIN _document_types dt ON d.document_type_id = dt.id
    JOIN _files f ON d.file_id = f.id
    JOIN _document_datas doc_data ON d.document_data_id = doc_data.id
    WHERE ad.application_id = %s
    """
    try:
        db.connect()
        db.cursor.execute(query, (application_id,))
        doc_tuples = db.cursor.fetchall()
        if doc_tuples:
            print(f"Fetched {len(doc_tuples)} documents for application {application_id}")
            return [Document.from_tuple(dt) for dt in doc_tuples]
        else:
            print(f"No documents found for application {application_id}")
            return []
    except Exception as e:
        print(f"Error fetching documents for application {application_id}: {e}")
        return []
    finally:
        db.close_conn()


def get_requirements_for_application(application_id) -> list[dict]:
    """Fetch all requirements linked to a given application ID."""
    query = """
    SELECT r.id, r.name, r.description
    FROM _requirements r
    JOIN _app_docs ad ON r.id = ad.requirements_id
    WHERE ad.application_id = %s
    """
    try:
        db.connect()
        db.cursor.execute(query, (application_id,))
        req_tuples = db.cursor.fetchall()
        print(f"Requirement tuples in candidate.get_requirements_for_application: {req_tuples}")
        requirements = []
        for rt in req_tuples:
            requirements.append({
                'id': rt[0],
                'name': rt[1],
                'description': rt[2]
            })
        print(f"Fetched {len(requirements)} requirements for application {application_id}")
        return requirements
    except Exception as e:
        print(f"Error fetching requirements for application {application_id}: {e}")
        return []
    finally:
        db.close_conn()


def get_document_details(document_id) -> Document:
    """Fetch detailed information for a specific document by its ID."""
    query = """
    SELECT 
        d.id AS document_id,
        d.file_id,
        dt.name AS document_type_name,
        f.filename,
        f.filepath,
        doc_data.ocr_full_text,
        d.last_modified,
        d.status_id
    FROM _documents d
    JOIN _document_types dt ON d.document_type_id = dt.id
    JOIN _files f ON d.file_id = f.id
    JOIN _document_datas doc_data ON d.document_data_id = doc_data.id
    WHERE d.id = %s
    """
    try:
        db.connect()
        db.cursor.execute(query, (document_id,))
        doc_tuple = db.cursor.fetchone()
        if doc_tuple:
            print(f"Fetched details for document {document_id}")
            return Document.from_tuple(doc_tuple)
        else:
            print(f"No details found for document {document_id}")
            return None
    except Exception as e:
        print(f"Error fetching details for document {document_id}: {e}")
        return None
    finally:
        db.close_conn()

#=== Routes

#======= Document Management Routes  =======

@login_required
@candidate_required
@candidate_bp.route("/dashboard/candidate/documentmanagement")
def document_management():
    # Get the application_id from the URL or session
    application_id = request.args.get('application_id')

    if not application_id:
        return redirect(url_for('candidate.applications_management'))  # If no application selected, redirect to applications page

    # Get requirements associated with the selected application
    requirements = get_requirements_for_application(application_id)

    # Get documents associated with the selected application
    documents = get_documents_for_application(application_id)

    return render_template(
        "candidate_documentmanagement.html",
        requirements=requirements,
        documents=documents,
        application_id=application_id  # Pass the application_id to the template
    )


@login_required
@candidate_required
@candidate_bp.route("/dashboard/candidate/documentmanagement/details/<document_id>")
def document_details(document_id):
    # Get the details of the selected document
    document = get_document_details(document_id)
    return render_template("candidate_documentdetails.html", document=document)



#======= Application Management Routes  =======

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

    print(f"Saving application: id={app_id}, user_id={user_id}, profession_id={profession_id}, country_id={country_id}, state_id={state_id}")

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

    try:
        db.connect()
        # Add all requirements for the profession, country and state to the application
        if selected_id:
            # Fetch all requirements for the selected profession, country, and state
            req_tuples = db.execute_query(
                """
                SELECT id FROM _requirements
                WHERE profession_id = %s AND country_id = %s AND (state_id = %s OR state_id IS NULL)
                """,
                (profession_id, country_id, state_id)
            )
            requirement_ids = [rt[0] for rt in req_tuples] if req_tuples else []
            print(f"Linking requirements {requirement_ids} to application {selected_id}")
            

            # Clear existing links
            db.execute_query(
                """
                DELETE FROM _app_docs
                WHERE application_id = %s
                """,
                (selected_id,)
            )
            # Link each requirement to the application    
            for req_id in requirement_ids:
                db.execute_query(
                    """
                    INSERT INTO _app_docs (id, application_id, document_id, requirements_id)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (str(uuid4()), selected_id, None, req_id)
                )
    except Exception as e:
        print(f"Error linking requirements to application {selected_id}: {e}")
    finally:
        db.close_conn()

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
