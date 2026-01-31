#****************************************************************************
#    Application:   Anerkennung AI Cockpit
#    Module:        frontend.webapp.candidate.routes
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.3
#****************************************************************************

#=== Imports
from uuid import uuid4
from types import SimpleNamespace
from flask import render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from backend.datamodule.models.document import Document
from frontend.webapp.candidate import candidate_bp
from frontend.webapp.utils import candidate_required
from backend.datamodule.models.profession import Profession
from backend.datamodule.models.country import Country
from backend.datamodule.models.state import State 
from backend.datamodule.models.application import Application
from backend.datamodule.models.requirements import Requirements
from backend.datamodule.models.document_data import DocumentData
from backend.datamodule.models.file import File as FileModel
from backend.datamodule.models.file_type import FileType
from backend.datamodule.models.status import Status
from backend.datamodule.models.document_type import DocumentType as DocumentTypeModel
from backend.datamodule.orm import AppDoc, Document as DocumentORM, DocumentData as DocumentDataORM, DocumentType, File, Status as StatusORM, Requirement
from backend.datamodule.sa import session_scope
from backend.services.ocr import analyze_bytes_with_layoutlm_fields
from werkzeug.utils import secure_filename
import os
import requests


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
                    StatusORM.name.label("status_name"),
                    AppDoc.requirements_id,
                )
                .join(DocumentORM, AppDoc.document_id == DocumentORM.id)
                .join(DocumentType, DocumentORM.document_type_id == DocumentType.id)
                .join(File, DocumentORM.file_id == File.id)
                .join(DocumentData, DocumentORM.document_data_id == DocumentData.id)
                .join(StatusORM, DocumentORM.status_id == StatusORM.id, isouter=True)
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
                        "status_name": row.status_name,
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
                    DocumentData.ocr_extracted_data,
                    DocumentORM.last_modified,
                    DocumentORM.status_id,
                    StatusORM.name.label("status_name"),
                )
                .join(DocumentType, DocumentORM.document_type_id == DocumentType.id)
                .join(File, DocumentORM.file_id == File.id)
                .join(DocumentData, DocumentORM.document_data_id == DocumentData.id)
                .join(StatusORM, DocumentORM.status_id == StatusORM.id, isouter=True)
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
                    "ocr_extracted_data": row.ocr_extracted_data or {},
                    "last_modified": row.last_modified,
                    "status_id": row.status_id,
                    "status_name": row.status_name,
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
@candidate_bp.route("/dashboard/candidate/documentmanagement", methods=["GET", "POST"])
def document_management():
    if request.method == "POST":
        application_id = request.form.get("application_id")
        requirement_id = request.form.get("requirement_id")
        file = request.files.get("document")

        if not application_id or not requirement_id or not file:
            flash("Missing application, requirement, or file.", "danger")
            return redirect(url_for("candidate.document_management", application_id=application_id))

        filename = secure_filename(file.filename)
        if not filename:
            flash("Invalid filename.", "danger")
            return redirect(url_for("candidate.document_management", application_id=application_id))

        file_bytes = file.read()
        if not file_bytes:
            flash("Empty file upload.", "danger")
            return redirect(url_for("candidate.document_management", application_id=application_id))

        upload_dir = current_app.config.get("UPLOAD_FOLDER", "backend/uploads")
        os.makedirs(upload_dir, exist_ok=True)
        stored_name = f"{uuid4().hex}_{filename}"
        stored_path = os.path.join(upload_dir, stored_name)
        with open(stored_path, "wb") as f:
            f.write(file_bytes)

        filetype_name = _infer_filetype(filename, file_bytes)
        filetype_tuple = FileType.get_by_name(filetype_name)
        filetype = FileType.from_tuple(filetype_tuple) if filetype_tuple else None

        doc_hint = _doc_hint_from_requirement(requirement_id)
        token_model_dir = _select_token_model_dir(doc_hint)
        ocr_service_url = os.getenv("OCR_SERVICE_URL")
        ocr_res = None
        fields = {}
        if ocr_service_url:
            try:
                remote = _call_ocr_service(ocr_service_url, file_bytes, filename, doc_hint)
                fields = remote.get("fields", remote)
                ocr_res = _coerce_remote_ocr(remote)
            except Exception:
                current_app.logger.warning("OCR service failed; using local OCR.", exc_info=True)
                ocr_res, fields = analyze_bytes_with_layoutlm_fields(file_bytes, token_model_dir=token_model_dir)
        if ocr_res is None:
            ocr_res, fields = analyze_bytes_with_layoutlm_fields(file_bytes, token_model_dir=token_model_dir)
        doc_type_name = _map_doc_type(ocr_res.doc_type, requirement_id)
        doc_type_tuple = DocumentTypeModel.get_by_name(doc_type_name) if doc_type_name else None
        doc_type = DocumentTypeModel.from_tuple(doc_type_tuple) if doc_type_tuple else None

        status_tuple = Status.get_by_name("new")
        status = Status.from_tuple(status_tuple) if status_tuple else None

        dd = DocumentData(
            ocr_doc_type_prediction=ocr_res.doc_type,
            ocr_predictions_str="\n".join(ocr_res.predictions) if isinstance(ocr_res.predictions, list) else ocr_res.predictions,
            ocr_full_text=ocr_res.ocr_text,
            ocr_extracted_data=fields,
        )
        dd_tuple = dd.insert()

        file_model = FileModel(
            filename=filename,
            filepath=stored_path,
            filetype_id=filetype.id if filetype else None,
        )
        file_tuple = file_model.insert()

        doc = Document(
            file_id=file_tuple[0],
            document_type_id=doc_type.id if doc_type else None,
            document_data_id=dd_tuple[0],
            user_id=current_user.id,
            status_id=status.id if status else None,
        )
        doc_tuple = doc.insert()

        with session_scope() as session:
            link = (
                session.query(AppDoc)
                .filter_by(application_id=application_id, requirements_id=requirement_id)
                .first()
            )
            if link:
                link.document_id = doc_tuple[0]
            else:
                session.add(AppDoc(
                    id=str(uuid4()),
                    application_id=application_id,
                    document_id=doc_tuple[0],
                    requirements_id=requirement_id,
                ))

        flash("Document uploaded and processed.", "success")
        return redirect(url_for("candidate.document_management", application_id=application_id))

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


@login_required
@candidate_required
@candidate_bp.post("/dashboard/candidate/documentmanagement/details/<document_id>/save")
def document_details_save(document_id):
    fields = {k: v for k, v in request.form.items() if k.startswith("field_")}
    if not fields:
        flash("No fields submitted.", "warning")
        return redirect(url_for("candidate.document_details", document_id=document_id))

    payload = {k.replace("field_", ""): v for k, v in fields.items()}
    with session_scope() as session:
        doc = session.query(DocumentORM).filter_by(id=document_id).first()
        if not doc or not doc.document_data_id:
            flash("Document not found.", "danger")
            return redirect(url_for("candidate.document_details", document_id=document_id))
        dd = session.query(DocumentDataORM).filter_by(id=doc.document_data_id).first()
        if not dd:
            flash("Document data not found.", "danger")
            return redirect(url_for("candidate.document_details", document_id=document_id))
        existing = dd.ocr_extracted_data or {}
        existing.update(payload)
        dd.ocr_extracted_data = existing

    flash("Fields updated.", "success")
    return redirect(url_for("candidate.document_details", document_id=document_id))


def _infer_filetype(filename: str, file_bytes: bytes) -> str:
    if file_bytes[:4] == b"%PDF":
        return "PDF"
    ext = os.path.splitext(filename.lower())[1]
    if ext in (".jpg", ".jpeg"):
        return "JPEG"
    if ext == ".png":
        return "PNG"
    return "PDF"


def _map_doc_type(doc_type: str, requirement_id: str) -> str | None:
    if doc_type:
        if doc_type.lower().startswith("passport"):
            return "passport"
        if "degree" in doc_type.lower() or "diploma" in doc_type.lower():
            return "diploma"
    # fallback: use requirement name
    req_tuple = Requirements.get_by_id(requirement_id)
    req = Requirements.from_tuple(req_tuple) if req_tuple else None
    if req and req.name and "id" in req.name.lower():
        return "passport"
    return None


def _doc_hint_from_requirement(requirement_id: str) -> str | None:
    req_tuple = Requirements.get_by_id(requirement_id)
    req = Requirements.from_tuple(req_tuple) if req_tuple else None
    if not req or not req.name:
        return None
    name = req.name.lower()
    if "id" in name or "passport" in name:
        return "passport"
    if "qualification" in name or "diploma" in name or "certificate" in name or "transcript" in name:
        return "diploma"
    return None


def _select_token_model_dir(doc_type_name: str | None) -> str | None:
    if not doc_type_name:
        return os.getenv("CAESAR_LAYOUTLM_TOKEN_MODEL_DIR")
    if "passport" in doc_type_name.lower():
        return os.getenv("CAESAR_PASSPORT_TOKEN_MODEL_DIR") or os.getenv("CAESAR_LAYOUTLM_TOKEN_MODEL_DIR")
    if "diploma" in doc_type_name.lower():
        return os.getenv("CAESAR_DIPLOMA_TOKEN_MODEL_DIR") or os.getenv("CAESAR_LAYOUTLM_TOKEN_MODEL_DIR")
    return os.getenv("CAESAR_LAYOUTLM_TOKEN_MODEL_DIR")


def _call_ocr_service(base_url: str, file_bytes: bytes, filename: str, doc_hint: str | None) -> dict:
    url = base_url.rstrip("/") + "/analyze"
    params = {}
    if doc_hint:
        params["doc_hint"] = doc_hint
    files = {"file": (filename, file_bytes)}
    resp = requests.post(url, params=params, files=files, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, dict):
        raise ValueError("OCR service response must be JSON object")
    return data


def _coerce_remote_ocr(remote: dict) -> SimpleNamespace:
    doc_type = remote.get("doc_type") or remote.get("document_type") or "unknown"
    ocr_text = remote.get("ocr_text") or remote.get("text") or remote.get("full_text") or ""
    predictions = remote.get("predictions") or remote.get("labels") or []
    return SimpleNamespace(doc_type=doc_type, ocr_text=ocr_text, predictions=predictions)



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
