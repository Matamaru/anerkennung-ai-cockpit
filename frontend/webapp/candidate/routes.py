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
from backend.datamodule.orm import AppDoc, Document as DocumentORM, DocumentData, DocumentType, File, Status, Requirement
from backend.datamodule.sa import session_scope


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
    try:
        with session_scope() as session:
            rows = (
                session.query(
                    AppDoc.document_id,
                    DocumentORM.file_id,
                    DocumentType.name.label("document_type_name"),
                    File.filename,
                    File.filepath,
                    DocumentData.ocr_full_text,
                    DocumentORM.status_id,
                    AppDoc.requirements_id,
                )
                .join(DocumentORM, AppDoc.document_id == DocumentORM.id)
                .join(DocumentType, DocumentORM.document_type_id == DocumentType.id)
                .join(File, DocumentORM.file_id == File.id)
                .join(DocumentData, DocumentORM.document_data_id == DocumentData.id)
                .filter(AppDoc.application_id == application_id)
                .all()
            )
            if rows:
                print(f"Fetched {len(rows)} documents for application {application_id}")
                return [
                    {
                        "document_id": row.document_id,
                        "file_id": row.file_id,
                        "document_type_name": row.document_type_name,
                        "filename": row.filename,
                        "filepath": row.filepath,
                        "ocr_full_text": row.ocr_full_text,
                        "status_id": row.status_id,
                        "requirements_id": row.requirements_id,
                    }
                    for row in rows
                ]
            print(f"No documents found for application {application_id}")
            return []
    except Exception as e:
        print(f"Error fetching documents for application {application_id}: {e}")
        return []


def get_requirements_for_application(application_id) -> list[dict]:
    """Fetch all requirements linked to a given application ID."""
    try:
        with session_scope() as session:
            rows = (
                session.query(Requirement.id, Requirement.name, Requirement.description)
                .join(AppDoc, Requirement.id == AppDoc.requirements_id)
                .filter(AppDoc.application_id == application_id)
                .all()
            )
            print(f"Requirement tuples in candidate.get_requirements_for_application: {rows}")
            requirements = [
                {"id": rt.id, "name": rt.name, "description": rt.description}
                for rt in rows
            ]
            print(f"Fetched {len(requirements)} requirements for application {application_id}")
            return requirements
    except Exception as e:
        print(f"Error fetching requirements for application {application_id}: {e}")
        return []


def get_document_details(document_id) -> Document:
    """Fetch detailed information for a specific document by its ID."""
    try:
        with session_scope() as session:
            row = (
                session.query(
                    DocumentORM.id.label("document_id"),
                    DocumentORM.file_id,
                    DocumentType.name.label("document_type_name"),
                    File.filename,
                    File.filepath,
                    DocumentData.ocr_full_text,
                    DocumentORM.last_modified,
                    DocumentORM.status_id,
                )
                .join(DocumentType, DocumentORM.document_type_id == DocumentType.id)
                .join(File, DocumentORM.file_id == File.id)
                .join(DocumentData, DocumentORM.document_data_id == DocumentData.id)
                .filter(DocumentORM.id == document_id)
                .first()
            )
            if row:
                print(f"Fetched details for document {document_id}")
                return {
                    "document_id": row.document_id,
                    "file_id": row.file_id,
                    "document_type_name": row.document_type_name,
                    "filename": row.filename,
                    "filepath": row.filepath,
                    "ocr_full_text": row.ocr_full_text,
                    "last_modified": row.last_modified,
                    "status_id": row.status_id,
                }
            print(f"No details found for document {document_id}")
            return None
    except Exception as e:
        print(f"Error fetching details for document {document_id}: {e}")
        return None

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
        # Add all requirements for the profession, country and state to the application
        if selected_id:
            with session_scope() as session:
                reqs = (
                    session.query(Requirement.id)
                    .filter(
                        Requirement.profession_id == profession_id,
                        Requirement.country_id == country_id,
                        (Requirement.state_id == state_id) | (Requirement.state_id.is_(None)),
                    )
                    .all()
                )
                requirement_ids = [rt.id for rt in reqs] if reqs else []
                print(f"Linking requirements {requirement_ids} to application {selected_id}")

                session.query(AppDoc).filter_by(application_id=selected_id).delete()
                for req_id in requirement_ids:
                    session.add(AppDoc(
                        id=str(uuid4()),
                        application_id=selected_id,
                        document_id=None,
                        requirements_id=req_id,
                    ))
    except Exception as e:
        print(f"Error linking requirements to application {selected_id}: {e}")

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
