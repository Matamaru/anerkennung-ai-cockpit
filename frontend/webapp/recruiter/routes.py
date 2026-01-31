#****************************************************************************
#    Application:   Anerkennung AI Cockpit
#    Module:        frontend.webapp.recruiter.routes
#    Author:        Heiko Matamaru, IGS
#    Version:       0.0.1
#****************************************************************************

#=== Imports
from flask import render_template, request, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from frontend.webapp.recruiter import recruiter_bp
from frontend.webapp.utils import recruiter_required
from backend.datamodule.sa import session_scope
from backend.datamodule.orm import (
    Application as ApplicationORM,
    Role as RoleORM,
    User as UserORM,
    AppDoc,
    Document as DocumentORM,
    DocumentData as DocumentDataORM,
    DocumentType,
    File,
    Requirement,
    Status as StatusORM,
)
from backend.datamodule.models.profession import Profession
from backend.datamodule.models.country import Country
from backend.datamodule.models.state import State
from sqlalchemy import func
import os
from frontend.webapp.candidate.routes import get_document_details, _build_document_form_fields
from backend.utils.s3_docs import presign_url, is_s3_uri

#=== Routes
@login_required
@recruiter_required
@recruiter_bp.route("/dashboard/recruiter/candidate-management")
def candidate_management():
    search = (request.args.get("q") or "").strip().lower()
    selected_user_id = request.args.get("user_id")
    selected_app_id = request.args.get("app_id")
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
        documents = []
        if selected_user_id:
            selected_user = (
                session.query(UserORM.user_id, UserORM.username, UserORM.email)
                .filter_by(user_id=selected_user_id)
                .first()
            )
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
            if selected_app_id:
                documents = (
                    session.query(
                        AppDoc.document_id,
                        Requirement.name.label("requirement_name"),
                        DocumentType.name.label("document_type_name"),
                        File.filename,
                        DocumentDataORM.ocr_full_text,
                        StatusORM.name.label("status_name"),
                    )
                    .join(DocumentORM, AppDoc.document_id == DocumentORM.id)
                    .join(Requirement, AppDoc.requirements_id == Requirement.id)
                    .join(DocumentType, DocumentORM.document_type_id == DocumentType.id, isouter=True)
                    .join(File, DocumentORM.file_id == File.id, isouter=True)
                    .join(DocumentDataORM, DocumentORM.document_data_id == DocumentDataORM.id, isouter=True)
                    .join(StatusORM, DocumentORM.status_id == StatusORM.id, isouter=True)
                    .filter(AppDoc.application_id == selected_app_id)
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
    documents_view = []
    for row in documents:
        if not row.document_id:
            continue
        documents_view.append(
            {
                "document_id": row.document_id,
                "requirement_name": row.requirement_name,
                "document_type_name": row.document_type_name,
                "filename": row.filename,
                "ocr_full_text": row.ocr_full_text,
                "status_name": row.status_name,
            }
        )

    selected_user_view = None
    if selected_user:
        selected_user_view = {
            "user_id": selected_user.user_id,
            "username": selected_user.username,
            "email": selected_user.email,
        }

    return render_template(
        "recruiter_candidatemanagement.html",
        candidates=candidates,
        query=search,
        selected_user=selected_user_view,
        selected_app_id=selected_app_id,
        applications=applications_view,
        documents=documents_view,
    )


@login_required
@recruiter_required
@recruiter_bp.get("/dashboard/recruiter/document/view/<document_id>")
def view_document(document_id):
    doc = get_document_details(document_id)
    if not doc:
        flash("Document not found.", "danger")
        return redirect(url_for("recruiter.candidate_management"))

    filepath = doc.get("filepath")
    filename = doc.get("filename") or "document"
    if is_s3_uri(filepath):
        url = presign_url(filepath)
        if url:
            return redirect(url)
        flash("Document file not found.", "danger")
        return redirect(url_for("recruiter.candidate_management"))

    if not filepath or not os.path.exists(filepath):
        flash("Document file not found.", "danger")
        return redirect(url_for("recruiter.candidate_management"))

    return send_file(filepath, as_attachment=False, download_name=filename)


@login_required
@recruiter_required
@recruiter_bp.get("/dashboard/recruiter/document/details/<document_id>")
def document_details(document_id):
    document = get_document_details(document_id)
    if not document:
        flash("Document not found.", "danger")
        return redirect(url_for("recruiter.candidate_management"))
    form_fields = _build_document_form_fields(document)
    return render_template("recruiter_documentdetails.html", document=document, form_fields=form_fields)


@login_required
@recruiter_required
@recruiter_bp.post("/dashboard/recruiter/document/details/<document_id>/review")
def document_review_save(document_id):
    status = (request.form.get("review_status") or "").strip().lower()
    comment = (request.form.get("review_comment") or "").strip()
    if status not in ("approved", "declined", "pending"):
        flash("Invalid review status.", "danger")
        return redirect(url_for("recruiter.document_details", document_id=document_id))
    if status == "declined" and not comment:
        flash("Comment is required when declining.", "danger")
        return redirect(url_for("recruiter.document_details", document_id=document_id))

    with session_scope() as session:
        doc = session.query(DocumentORM).filter_by(id=document_id).first()
        if not doc or not doc.document_data_id:
            flash("Document not found.", "danger")
            return redirect(url_for("recruiter.candidate_management"))
        dd = session.query(DocumentDataORM).filter_by(id=doc.document_data_id).first()
        if not dd:
            flash("Document data not found.", "danger")
            return redirect(url_for("recruiter.candidate_management"))
        dd.review_status = status
        dd.review_comment = comment or None
        dd.reviewed_by = current_user.id
        dd.reviewed_at = func.now()

    flash("Review saved.", "success")
    return redirect(url_for("recruiter.document_details", document_id=document_id))

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
