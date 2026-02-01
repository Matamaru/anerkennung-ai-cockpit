#****************************************************************************
#    Application:   Anerkennung AI Cockpit
#    Module:        frontend.webapp.candidate.routes
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.3
#****************************************************************************

#=== Imports
from uuid import uuid4
from types import SimpleNamespace
from flask import render_template, request, redirect, url_for, flash, current_app, send_file
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
from backend.datamodule.orm import AppDoc, Document as DocumentORM, DocumentData as DocumentDataORM, DocumentType, File, Status as StatusORM, Requirement, UserProfile as UserProfileORM
from backend.datamodule.sa import session_scope
from backend.services.ocr import (
    analyze_bytes_with_layoutlm_fields,
    _extract_mrz_from_text,
    _postprocess_passport_fields,
    extract_diploma_fields,
)
from backend.utils.s3_docs import upload_bytes, presign_url, is_s3_uri
from werkzeug.utils import secure_filename
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm.attributes import flag_modified
import difflib
import re
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
                    DocumentDataORM.ocr_full_text,
                    DocumentDataORM.review_status,
                    DocumentORM.status_id,
                    StatusORM.name.label("status_name"),
                    AppDoc.requirements_id,
                )
                .join(DocumentORM, AppDoc.document_id == DocumentORM.id)
                .join(DocumentType, DocumentORM.document_type_id == DocumentType.id)
                .join(File, DocumentORM.file_id == File.id)
                .join(DocumentDataORM, DocumentORM.document_data_id == DocumentDataORM.id)
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
                        "review_status": row.review_status,
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
                .distinct(Requirement.id)
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


def _requirement_allows_multiple(requirement_id: str) -> bool:
    req_tuple = Requirements.get_by_id(requirement_id)
    req = Requirements.from_tuple(req_tuple) if req_tuple else None
    if not req or not req.name:
        return False
    if getattr(req, "allow_multiple", None) is not None:
        return bool(req.allow_multiple)
    name = req.name.lower()
    if name in ("id", "cv", "proofofberlinresponsibility", "passport"):
        return False
    return True


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
                    DocumentDataORM.ocr_full_text,
                    DocumentDataORM.ocr_extracted_data,
                    DocumentDataORM.ocr_source,
                    DocumentDataORM.check_ready,
                    DocumentDataORM.validation_errors,
                    DocumentDataORM.review_status,
                    DocumentDataORM.review_comment,
                    DocumentDataORM.reviewed_by,
                    DocumentDataORM.reviewed_at,
                    DocumentDataORM.check_ready,
                    DocumentDataORM.validation_errors,
                    DocumentORM.last_modified,
                    DocumentORM.status_id,
                    StatusORM.name.label("status_name"),
                )
                .join(DocumentType, DocumentORM.document_type_id == DocumentType.id)
                .join(File, DocumentORM.file_id == File.id)
                .join(DocumentDataORM, DocumentORM.document_data_id == DocumentDataORM.id)
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
                    "ocr_source": row.ocr_source,
                    "check_ready": row.check_ready,
                    "validation_errors": row.validation_errors,
                    "review_status": row.review_status,
                    "review_comment": row.review_comment,
                    "reviewed_by": row.reviewed_by,
                    "reviewed_at": row.reviewed_at,
                    "check_ready": row.check_ready,
                    "validation_errors": row.validation_errors,
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
        s3_uri = upload_bytes(file_bytes, stored_name, user_id=current_user.id)
        if s3_uri:
            stored_path = s3_uri
            try:
                os.remove(os.path.join(upload_dir, stored_name))
            except Exception:
                pass

        filetype_name = _infer_filetype(filename, file_bytes)
        filetype_tuple = FileType.get_by_name(filetype_name)
        filetype = FileType.from_tuple(filetype_tuple) if filetype_tuple else None

        doc_hint = _doc_hint_from_requirement(requirement_id) or _doc_hint_from_filename(filename)
        token_model_dir = _select_token_model_dir(doc_hint)
        ocr_service_url = os.getenv("OCR_SERVICE_URL")
        ocr_res = None
        fields = {}
        ocr_source = "local"
        if ocr_service_url:
            try:
                remote = _call_ocr_service(ocr_service_url, file_bytes, filename, doc_hint)
                fields = remote.get("fields", remote)
                ocr_res = _coerce_remote_ocr(remote)
                ocr_source = "remote"
            except Exception:
                current_app.logger.warning("OCR service failed; using local OCR.", exc_info=True)
                ocr_res, fields = analyze_bytes_with_layoutlm_fields(file_bytes, token_model_dir=token_model_dir)
        if ocr_res is None:
            ocr_res, fields = analyze_bytes_with_layoutlm_fields(file_bytes, token_model_dir=token_model_dir)
        if not fields and getattr(ocr_res, "fields", None):
            fields = ocr_res.fields
        fields, check_ready, validation_errors = _evaluate_document_fields(doc_type_name=_map_doc_type(ocr_res.doc_type, requirement_id), fields=fields)
        ocr_text = getattr(ocr_res, "ocr_text", "") or ""
        current_app.logger.warning(
            "OCR result (%s) for %s: doc_type=%s text_len=%s fields=%s",
            ocr_source,
            filename,
            getattr(ocr_res, "doc_type", "unknown"),
            len(ocr_text),
            len(fields or {}),
        )
        if not ocr_text:
            current_app.logger.warning("OCR text is empty for %s", filename)
        if not fields:
            current_app.logger.warning("OCR extracted fields are empty for %s", filename)
            if ocr_text:
                mrz_fields = _extract_mrz_from_text(ocr_text)
                if mrz_fields:
                    fields = _postprocess_passport_fields(mrz_fields)
                    if fields.get("mrz_checksum_ok") is False:
                        fields = _drop_mrz_fields(fields)
                        fields.update(_extract_passport_text_fields(ocr_text))
                    current_app.logger.info("OCR fallback extracted MRZ fields for %s", filename)
                elif doc_hint in ("diploma", "degree"):
                    diploma_fields = extract_diploma_fields(ocr_text)
                    if diploma_fields:
                        fields = diploma_fields
                        current_app.logger.info("OCR fallback extracted diploma fields for %s", filename)
                if not fields:
                    fields = {"ocr_text": ocr_text}
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
            ocr_source=ocr_source,
            check_ready=check_ready,
            validation_errors=validation_errors,
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
            if link and not _requirement_allows_multiple(requirement_id):
                link.document_id = doc_tuple[0]
            else:
                session.add(
                    AppDoc(
                        id=str(uuid4()),
                        application_id=application_id,
                        document_id=doc_tuple[0],
                        requirements_id=requirement_id,
                    )
                )

        flash("Document uploaded and processed.", "success")
        return redirect(url_for("candidate.document_management", application_id=application_id))

    # Get the application_id from the URL or session
    application_id = request.args.get('application_id')

    app_tuple = Application.get_by_user_id(current_user.id)
    applications = [Application.from_tuple(a) for a in app_tuple] if app_tuple else []
    professions, countries, states = _load_select_data()
    applications = _attach_display_data(applications, professions, countries, states)

    requirements = []
    documents = []
    review_alerts = []
    application_check_ready = False
    if application_id:
        # Get requirements associated with the selected application
        requirements = get_requirements_for_application(application_id)

        # Get documents associated with the selected application
        documents = get_documents_for_application(application_id)
        review_alerts = [
            d for d in documents if (d.get("review_status") or "pending") in ("approved", "declined")
        ]
        application_check_ready = _application_check_ready(application_id, requirements, documents)

    return render_template(
        "candidate_documentmanagement.html",
        applications=applications,
        requirements=requirements,
        documents=documents,
        application_id=application_id,  # Pass the application_id to the template
        review_alerts=review_alerts,
        application_check_ready=application_check_ready,
    )


@login_required
@candidate_required
@candidate_bp.route("/dashboard/candidate/documentmanagement/details/<document_id>")
def document_details(document_id):
    # Get the details of the selected document
    document = get_document_details(document_id)
    profile = _get_user_profile(current_user.id)
    form_fields = _build_document_form_fields(document, profile)
    return render_template(
        "candidate_documentdetails.html",
        document=document,
        form_fields=form_fields,
        profile=profile,
    )


@login_required
@candidate_required
@candidate_bp.get("/dashboard/candidate/documentmanagement/view/<document_id>")
def view_document(document_id):
    with session_scope() as session:
        doc = session.query(DocumentORM).filter_by(id=document_id).first()
        if not doc:
            flash("Document not found.", "danger")
            return redirect(url_for("candidate.document_management"))
        if doc.user_id and str(doc.user_id) != str(current_user.id):
            flash("Not allowed to view this document.", "danger")
            return redirect(url_for("candidate.document_management"))
        file_row = session.query(File).filter_by(id=doc.file_id).first() if doc.file_id else None
        filepath = file_row.filepath if file_row else None
        filename = file_row.filename if file_row else "document"

    if is_s3_uri(filepath):
        url = presign_url(filepath)
        if url:
            return redirect(url)
        flash("Document file not found.", "danger")
        return redirect(url_for("candidate.document_details", document_id=document_id))

    if not filepath or not os.path.exists(filepath):
        flash("Document file not found.", "danger")
        return redirect(url_for("candidate.document_details", document_id=document_id))

    return send_file(filepath, as_attachment=False, download_name=filename)


@login_required
@candidate_required
@candidate_bp.post("/dashboard/candidate/documentmanagement/details/<document_id>/save")
def document_details_save(document_id):
    fields = {k: v for k, v in request.form.items() if k.startswith("field_")}
    application_id = request.form.get("application_id")
    profile_fields_raw = request.form.get("profile_fields") or ""
    payload = {}
    for key, value in fields.items():
        cleaned = (value or "").strip()
        if cleaned:
            payload[key.replace("field_", "")] = cleaned

    profile_keys = [k.strip() for k in profile_fields_raw.split(",") if k.strip()]
    if profile_keys:
        profile = _get_user_profile(current_user.id)
        for key in profile_keys:
            if key in payload:
                continue
            profile_value = _profile_value_for_field(key, profile)
            if profile_value:
                payload[key] = profile_value
    if not payload:
        flash("No fields submitted.", "warning")
        return redirect(url_for("candidate.document_details", document_id=document_id, application_id=application_id))

    with session_scope() as session:
        doc = session.query(DocumentORM).filter_by(id=document_id).first()
        if not doc or not doc.document_data_id:
            flash("Document not found.", "danger")
            return redirect(url_for("candidate.document_details", document_id=document_id, application_id=application_id))
        dd = session.query(DocumentDataORM).filter_by(id=doc.document_data_id).first()
        if not dd:
            flash("Document data not found.", "danger")
            return redirect(url_for("candidate.document_details", document_id=document_id, application_id=application_id))
        existing = dict(dd.ocr_extracted_data or {})
        existing.update(payload)
        updated_fields, check_ready, validation_errors = _evaluate_document_fields(
            doc_type_name=doc.document_type.name if doc.document_type else None,
            fields=existing,
        )
        dd.ocr_extracted_data = dict(updated_fields)
        flag_modified(dd, "ocr_extracted_data")
        dd.check_ready = check_ready
        dd.validation_errors = validation_errors

    flash("Fields updated.", "success")
    return redirect(url_for("candidate.document_details", document_id=document_id, application_id=application_id))


@login_required
@candidate_required
@candidate_bp.post("/dashboard/candidate/documentmanagement/delete/<document_id>")
def delete_document(document_id):
    application_id = request.form.get("application_id")
    with session_scope() as session:
        doc = session.query(DocumentORM).filter_by(id=document_id).first()
        if not doc:
            flash("Document not found.", "danger")
            return redirect(url_for("candidate.document_management", application_id=application_id))
        if doc.user_id and str(doc.user_id) != str(current_user.id):
            flash("Not allowed to delete this document.", "danger")
            return redirect(url_for("candidate.document_management", application_id=application_id))

        app_docs = session.query(AppDoc).filter_by(document_id=document_id).all()
        if not application_id and app_docs:
            application_id = app_docs[0].application_id
        for ad in app_docs:
            ad.document_id = None

        file_id = doc.file_id
        data_id = doc.document_data_id
        filepath = doc.file.filepath if doc.file else None
        session.delete(doc)

        if file_id:
            still_used = session.query(DocumentORM).filter_by(file_id=file_id).first()
            if not still_used:
                file_row = session.query(File).filter_by(id=file_id).first()
                if file_row:
                    session.delete(file_row)
        if data_id:
            still_used = session.query(DocumentORM).filter_by(document_data_id=data_id).first()
            if not still_used:
                data_row = session.query(DocumentDataORM).filter_by(id=data_id).first()
                if data_row:
                    session.delete(data_row)

    if filepath and not is_s3_uri(filepath) and os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception:
            pass

    flash("Document deleted.", "success")
    return redirect(url_for("candidate.document_management", application_id=application_id))


def _infer_filetype(filename: str, file_bytes: bytes) -> str:
    if file_bytes[:4] == b"%PDF":
        return "PDF"
    ext = os.path.splitext(filename.lower())[1]
    if ext in (".jpg", ".jpeg"):
        return "JPEG"
    if ext == ".png":
        return "PNG"
    return "PDF"


def _pick_field_value(fields: dict, keys: list[str], default: str = "") -> str:
    for key in keys:
        if key in fields and fields[key] not in (None, ""):
            val = fields[key]
            if isinstance(val, list):
                return ", ".join(str(v) for v in val if v not in (None, ""))
            return str(val)
    return default


def _sanitize_field_value(key: str, value: str, fields: dict) -> str:
    cleaned = (value or "").strip()
    if not cleaned:
        return ""
    lower_key = key.lower()
    if fields.get("mrz_checksum_ok") is False and lower_key in {
        "birth_date",
        "expiry_date",
        "passport_number",
        "nationality",
        "issuing_country",
        "personal_number",
        "sex",
    }:
        return ""
    if "name" in lower_key:
        cleaned = cleaned.replace("<", " ")
        cleaned = " ".join(cleaned.split())
    elif any(token in lower_key for token in ("nationality", "issuing_country", "passport_number", "personal_number", "sex")):
        cleaned = cleaned.replace("<", "")
        cleaned = re.sub(r"[^A-Za-z0-9]", "", cleaned)
        if "nationality" in lower_key or "issuing_country" in lower_key:
            cleaned = cleaned.upper()
            if not re.fullmatch(r"[A-Z]{3}", cleaned or ""):
                return ""
        elif "passport_number" in lower_key:
            cleaned = cleaned.upper()
            if not re.fullmatch(r"[A-Z0-9]{6,9}", cleaned or ""):
                return ""
        elif "personal_number" in lower_key:
            cleaned = cleaned.upper()
            if cleaned and not re.fullmatch(r"[A-Z0-9]{1,14}", cleaned):
                return ""
        elif lower_key == "sex":
            cleaned = cleaned.upper()
            if cleaned and cleaned not in {"M", "F", "X"}:
                return ""
    elif "date" in lower_key:
        cleaned = cleaned.replace("<", "")
        digits = re.sub(r"[^0-9]", "", cleaned)
        if len(digits) == 6:
            yy = int(digits[:2])
            mm = digits[2:4]
            dd = digits[4:6]
            current_yy = datetime.utcnow().year % 100
            century = 2000 if yy <= current_yy else 1900
            cleaned = f"{century + yy:04d}-{mm}-{dd}"
        elif len(digits) == 8:
            cleaned = f"{digits[:4]}-{digits[4:6]}-{digits[6:8]}"
        else:
            cleaned = digits or cleaned
        if cleaned and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", cleaned):
            return ""
    else:
        cleaned = cleaned.replace("<", "").strip()
    return cleaned


def _extract_passport_text_fields(ocr_text: str) -> dict:
    if not ocr_text:
        return {}
    out: dict = {}
    m = re.search(r"\bname\s*[:\-]\s*([A-ZÄÖÜ][A-Za-zÄÖÜäöüß.\-\s]{2,80})", ocr_text, re.I)
    if m:
        full = " ".join(m.group(1).split())
        parts = full.split()
        if parts:
            out["surname"] = parts[-1]
            out["given_names"] = " ".join(parts[:-1]) if len(parts) > 1 else ""
            out["full_name"] = full
    m = re.search(r"\bnationality\s*[:\-]\s*([A-Z]{3})\b", ocr_text, re.I)
    if m:
        out["nationality"] = m.group(1).upper()
    m = re.search(r"\b(passport|passnummer|passport no)\s*[:\-]?\s*([A-Z0-9]{6,9})\b", ocr_text, re.I)
    if m:
        out["passport_number"] = m.group(2).upper()
    return out


def _drop_mrz_fields(fields: dict) -> dict:
    if not isinstance(fields, dict):
        return {}
    cleaned = dict(fields)
    for key in (
        "document_code",
        "issuing_country",
        "passport_number",
        "passport_number_check",
        "nationality",
        "birth_date",
        "birth_date_check",
        "expiry_date",
        "expiry_date_check",
        "sex",
        "personal_number",
        "personal_number_check",
        "final_check",
        "surname",
        "given_names",
        "full_name",
    ):
        cleaned.pop(key, None)
    return cleaned


def _document_form_schema(doc_type_name: str | None) -> list[dict]:
    dtype = (doc_type_name or "").lower()
    if "passport" in dtype or "id" in dtype:
        return [
            {"key": "given_names", "label": "First Name(s)", "source_keys": ["given_names"]},
            {"key": "surname", "label": "Last Name", "source_keys": ["surname"]},
            {"key": "surname_birth", "label": "Birth/Former Name", "source_keys": ["surname_birth", "surname_previous"]},
            {"key": "nationality", "label": "Nationality", "source_keys": ["nationality"]},
            {"key": "passport_number", "label": "Passport Number", "source_keys": ["passport_number", "document_number"]},
            {"key": "birth_date", "label": "Birth Date (YYYY-MM-DD)", "source_keys": ["birth_date", "birth_date_raw"]},
            {"key": "sex", "label": "Sex", "source_keys": ["sex"]},
            {"key": "expiry_date", "label": "Expiry Date (YYYY-MM-DD)", "source_keys": ["expiry_date", "expiry_date_raw"]},
            {"key": "issuing_country", "label": "Issuing Country", "source_keys": ["issuing_country"]},
            {"key": "personal_number", "label": "Personal Number", "source_keys": ["personal_number"]},
        ]
    if "diploma" in dtype or "degree" in dtype or "certificate" in dtype:
        return [
            {"key": "holder_first_name", "label": "First Name(s)", "source_keys": ["holder_first_name"]},
            {"key": "holder_last_name", "label": "Last Name", "source_keys": ["holder_last_name"]},
            {"key": "holder_name", "label": "Full Name", "source_keys": ["holder_name", "holder_name_guess", "holder_full_name"]},
            {"key": "holder_birth_name", "label": "Birth/Former Name", "source_keys": ["holder_birth_name"]},
            {"key": "institution_name", "label": "Institution", "source_keys": ["institution_name", "institution", "institution_guess", "institution_label"]},
            {"key": "degree_type", "label": "Degree Type", "source_keys": ["degree_type", "degree_type_guess"]},
            {"key": "program_or_field", "label": "Program / Field", "source_keys": ["program_or_field", "program_guess", "field_of_study"]},
            {"key": "graduation_status", "label": "Graduation Status", "source_keys": ["graduation_status"]},
            {"key": "graduation_date", "label": "Graduation Date", "source_keys": ["graduation_date", "issue_date_guess", "dates", "dates_detected"]},
            {"key": "location", "label": "Location", "source_keys": ["location", "location_guess"]},
            {"key": "diploma_number", "label": "Diploma Number", "source_keys": ["diploma_number", "diploma_number_guess"]},
        ]
    return []


def _build_document_form_fields(document: dict | None, profile: dict | None = None) -> list[dict]:
    if not document:
        return []
    fields = document.get("ocr_extracted_data") or {}
    schema = _document_form_schema(document.get("document_type_name"))
    mandatory = set(_mandatory_fields_for_doc_type(document.get("document_type_name")))
    error_list = (document.get("validation_errors") or {}).get("errors", []) if document else []
    if not schema:
        raw_fields = [
            {"key": key, "label": key.replace("_", " ").title(), "value": str(value)}
            for key, value in fields.items()
        ]
        out = []
        for f in raw_fields:
            f["required"] = f["key"] in mandatory
            f["ready"] = (not f["required"]) or (f.get("value") not in ("", None))
            f["errors"] = [e for e in error_list if f["key"] in e]
            out.append(_attach_profile_suggestion(f, profile))
        return out
    out: list[dict] = []
    for entry in schema:
        key = entry["key"]
        field = {
            "key": key,
            "label": entry["label"],
            "value": _sanitize_field_value(
                key,
                _pick_field_value(fields, entry.get("source_keys", [key])),
                fields,
            ),
        }
        field["required"] = key in mandatory
        field["ready"] = (not field["required"]) or (field.get("value") not in ("", None))
        field["errors"] = [e for e in error_list if key in e]
        out.append(_attach_profile_suggestion(field, profile))
    return out


def _mandatory_fields_for_doc_type(doc_type_name: str | None) -> list[str]:
    name = (doc_type_name or "").lower()
    if "passport" in name or name == "id":
        return [
            "surname",
            "given_names",
            "nationality",
            "passport_number",
            "birth_date",
            "sex",
            "expiry_date",
            "issuing_country",
        ]
    return []


def _normalize_date_field(value: str) -> str | None:
    cleaned = (value or "").strip()
    if not cleaned:
        return None
    # Accept YYYY-MM-DD
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", cleaned):
        return cleaned
    # Accept DD.MM.YYYY
    m = re.fullmatch(r"(\d{2})\.(\d{2})\.(\d{4})", cleaned)
    if m:
        return f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
    # Accept YYYY/MM/DD or DD/MM/YYYY
    m = re.fullmatch(r"(\d{2,4})/(\d{2})/(\d{2,4})", cleaned)
    if m:
        a, b, c = m.group(1), m.group(2), m.group(3)
        if len(a) == 4:
            return f"{a}-{b}-{c.zfill(2)}"
        if len(c) == 4:
            return f"{c}-{b}-{a.zfill(2)}"
    return None


def _evaluate_document_fields(doc_type_name: str | None, fields: dict) -> tuple[dict, bool, dict]:
    errors: list[str] = []
    updated = dict(fields or {})
    mandatory = _mandatory_fields_for_doc_type(doc_type_name)

    # Normalize key fields for passport
    if mandatory:
        if "birth_date" in updated:
            normalized = _normalize_date_field(str(updated.get("birth_date") or ""))
            if normalized:
                updated["birth_date"] = normalized
        if "expiry_date" in updated:
            normalized = _normalize_date_field(str(updated.get("expiry_date") or ""))
            if normalized:
                updated["expiry_date"] = normalized

        if "nationality" in updated and updated.get("nationality"):
            updated["nationality"] = str(updated["nationality"]).upper().strip()
        if "issuing_country" in updated and updated.get("issuing_country"):
            updated["issuing_country"] = str(updated["issuing_country"]).upper().strip()
        if "passport_number" in updated and updated.get("passport_number"):
            updated["passport_number"] = str(updated["passport_number"]).upper().strip()
        if "sex" in updated and updated.get("sex"):
            updated["sex"] = str(updated["sex"]).upper().strip()

        # Validate mandatory fields
        for key in mandatory:
            if not updated.get(key):
                errors.append(f"{key} is missing")

        if updated.get("nationality") and not re.fullmatch(r"[A-Z]{3}", updated["nationality"]):
            errors.append("nationality is invalid")
        if updated.get("issuing_country") and not re.fullmatch(r"[A-Z]{3}", updated["issuing_country"]):
            errors.append("issuing_country is invalid")
        if updated.get("passport_number") and not re.fullmatch(r"[A-Z0-9]{6,9}", updated["passport_number"]):
            errors.append("passport_number is invalid")
        if updated.get("sex") and updated["sex"] not in {"M", "F", "X"}:
            errors.append("sex is invalid")
        for date_key in ("birth_date", "expiry_date"):
            if updated.get(date_key) and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", updated[date_key]):
                errors.append(f"{date_key} is invalid")

    check_ready = (len(errors) == 0) if mandatory else True
    return updated, check_ready, {"errors": errors}


def _application_check_ready(application_id: str, requirements: list[dict], documents: list[dict]) -> bool:
    if not application_id:
        return False
    required_ids = {r["id"] for r in requirements}
    if not required_ids:
        return False
    ready_requirements = set()
    for doc in documents:
        if doc.get("requirements_id") in required_ids and doc.get("check_ready"):
            ready_requirements.add(doc.get("requirements_id"))
    return required_ids.issubset(ready_requirements)


def _get_user_profile(user_id: str) -> dict | None:
    with session_scope() as session:
        row = session.query(UserProfileORM).filter_by(user_id=user_id).first()
        if not row:
            return None
        return {
            "user_id": row.user_id,
            "first_name": row.first_name,
            "last_name": row.last_name,
            "birth_date": row.birth_date,
            "nationality": row.nationality,
            "address_line1": row.address_line1,
            "address_line2": row.address_line2,
            "postal_code": row.postal_code,
            "city": row.city,
            "country": row.country,
            "phone": row.phone,
        }


def _normalize_compare(value: str) -> str:
    value = (value or "").lower()
    value = re.sub(r"[^a-z0-9]", "", value)
    return value


def _similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, _normalize_compare(a), _normalize_compare(b)).ratio()


def _profile_value_for_field(field_key: str, profile: dict | None) -> str | None:
    if not profile:
        return None
    key = (field_key or "").lower()
    if key in ("given_names", "holder_first_name"):
        return profile.get("first_name")
    if key in ("surname", "holder_last_name"):
        return profile.get("last_name")
    if key in ("holder_name", "full_name"):
        first = profile.get("first_name") or ""
        last = profile.get("last_name") or ""
        full = f"{first} {last}".strip()
        return full or None
    if key in ("birth_date", "date_of_birth"):
        return profile.get("birth_date")
    if key == "nationality":
        return profile.get("nationality")
    return None


def _attach_profile_suggestion(field: dict, profile: dict | None) -> dict:
    profile_value = _profile_value_for_field(field.get("key", ""), profile)
    field_value = field.get("value") or ""
    if profile_value:
        score = _similarity(field_value, profile_value) if field_value else 0.0
        field["profile_value"] = profile_value
        field["profile_match_score"] = score
    return field


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


def _doc_hint_from_filename(filename: str) -> str | None:
    name = (filename or "").lower()
    if "passport" in name or name.startswith("pass"):
        return "passport"
    if "diploma" in name or "degree" in name or "certificate" in name or "transcript" in name:
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
    timeout_s = int(os.getenv("OCR_SERVICE_TIMEOUT", "15"))
    resp = requests.post(url, params=params, files=files, timeout=(5, timeout_s))
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
@candidate_bp.route("/dashboard/candidate/profile", methods=["GET", "POST"])
def candidate_profile():
    if request.method == "POST":
        payload = {
            "first_name": request.form.get("first_name") or None,
            "last_name": request.form.get("last_name") or None,
            "birth_date": request.form.get("birth_date") or None,
            "nationality": request.form.get("nationality") or None,
            "address_line1": request.form.get("address_line1") or None,
            "address_line2": request.form.get("address_line2") or None,
            "postal_code": request.form.get("postal_code") or None,
            "city": request.form.get("city") or None,
            "country": request.form.get("country") or None,
            "phone": request.form.get("phone") or None,
        }
        with session_scope() as session:
            profile = session.query(UserProfileORM).filter_by(user_id=current_user.id).first()
            if not profile:
                profile = UserProfileORM(user_id=current_user.id, **payload)
                session.add(profile)
            else:
                for key, value in payload.items():
                    setattr(profile, key, value)
            profile.updated_at = func.now()
        flash("Profile updated.", "success")
        return redirect(url_for("candidate.candidate_profile"))

    profile = _get_user_profile(current_user.id) or {}
    return render_template("candidate_profile.html", profile=profile)


@login_required
@candidate_required
@candidate_bp.route("/dashboard/candidate/contact-recruiter")
def contact_recruiter():
    return render_template("candidate_contactrecruiter.html")
